// SPDX-License-Identifier: MIT
//
// clinic_py/monitor.c
//
// This file implements a resource usage sampler as a CPython
// extension module.  The sampler starts a detached POSIX thread that
// periodically samples process level metrics such as CPU usage, memory
// consumption and context switch counters using getrusage().
//
// In the original version of this file samples were emitted as CSV
// lines to stdout or a user‑specified file.  That worked well for
// simple metrics but becomes difficult to extend as more fields are
// added and higher sampling rates are used.  To support richer data
// collection without incurring significant overhead the sampler now
// writes a binary file when a filepath is provided.  Each record in
// the binary file has a fixed layout defined by the MetricRecord
// structure below.  A small header is written when the file is
// opened to allow future versioning.
//
// Metrics are now always written to a binary file.  The CSV output
// to stdout from earlier versions has been removed to simplify the
// format and avoid performance overhead.  When no filepath is
// provided the default file 'metrics.bin' is used.  The binary
// format is cross‑platform friendly and can be parsed by Python code
// using the struct module.

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stddef.h>
#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <string.h>

#ifdef __unix__
# include <pthread.h>
# include <unistd.h>
# include <sys/resource.h>
# include <errno.h>
#endif

// Record layout for binary metric samples.  Changing this structure
// requires bumping the version number in FileHeader.  In addition to
// process level metrics, each record now contains aggregate counts of
// Python stack frames sampled across all threads.  These counts
// categorize frames into user application code, third‑party library
// code located in site‑packages and code residing in the Python
// standard library or builtin modules.  Aggregating counts reduces
// overhead versus capturing full call stacks on every sample.
typedef struct {
    double timestamp;       // seconds since start of sampling
    double user_time;       // user CPU time in seconds
    double system_time;     // system CPU time in seconds
    long rss_kb;            // resident set size in KiB
    long inblock;           // number of block input operations
    long oublock;           // number of block output operations
    long nvcsw;             // number of voluntary context switches
    long nivcsw;            // number of involuntary context switches
    long py_app_frames;     // aggregated count of Python frames in application code
    long py_lib_frames;     // aggregated count of Python frames in third‑party libraries
    long py_core_frames;    // aggregated count of Python frames in Python stdlib/core
} MetricRecord;

// Header written to the beginning of a binary metrics file.  The
// "magic" field identifies this as a clinic_py metrics file and the
// version string allows the format to evolve in the future.  The
// header is padded to 64 bytes to leave space for additional
// metadata.
typedef struct {
    char magic[8];        // set to "CLINICPY" to identify the file
    uint8_t version;      // format version (currently 2)
    uint8_t reserved[55]; // reserved/padding bytes
} FileHeader;

// Global state for the monitor thread.
static int monitoring = 0;
#ifdef __unix__
static pthread_t monitor_thread;
#endif
static FILE *metrics_fp = NULL;
static double start_time = 0.0;

// Python‑related state used to categorize call stacks.  These globals
// are initialized lazily when the profiler starts.  app_base_path is
// a user supplied prefix that identifies application code.  Any
// filename beginning with this prefix is considered to belong to the
// user’s own code.  site_packages_paths is an array of prefixes
// corresponding to directories returned from site.getsitepackages().
// sys_prefix_str holds sys.prefix which identifies the standard
// library location.  current_frames_func references the
// sys._current_frames function so that we can sample stack frames
// without repeatedly importing sys.  A simple flag ensures that
// initialization is performed only once per process.
static char *app_base_path = NULL;
static char **site_packages_paths = NULL;
static int num_site_packages = 0;
static char *sys_prefix_str = NULL;
static PyObject *current_frames_func = NULL;
static int paths_initialized = 0;

// Forward declaration of helper to initialise Python paths.  Returns 0
// on success and -1 on failure (with an appropriate Python
// exception set).  Must be called with the GIL held.
static int init_python_paths(void);

// Helper to free path data on interpreter finalisation.  Not
// registered with Py_AtExit; called implicitly when monitor stops.
static void free_python_paths(void) {
    if (site_packages_paths) {
        for (int i = 0; i < num_site_packages; i++) {
            free(site_packages_paths[i]);
        }
        free(site_packages_paths);
        site_packages_paths = NULL;
    }
    num_site_packages = 0;
    free(sys_prefix_str);
    sys_prefix_str = NULL;
    if (current_frames_func) {
        Py_DECREF(current_frames_func);
        current_frames_func = NULL;
    }
    free(app_base_path);
    app_base_path = NULL;
    paths_initialized = 0;
}

// Helper to get a monotonic timestamp as a double in seconds.
static double now_monotonic(void) {
    struct timespec ts;
#ifdef CLOCK_MONOTONIC
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
#else
    // Fallback to CLOCK_REALTIME on platforms without CLOCK_MONOTONIC.
    clock_gettime(CLOCK_REALTIME, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
#endif
}

// Initialise the Python path prefixes used for categorising stack frames.
// This helper imports the sys and site modules, obtains sys.prefix and
// site.getsitepackages(), and stores them as C strings.  It also
// retrieves sys._current_frames.  Because this function uses the
// Python C API it must be called with the GIL held.  On success
// returns 0; on failure returns -1 and leaves a Python exception set.
static int init_python_paths(void) {
    if (paths_initialized) {
        return 0;
    }
    // Import sys module
    PyObject *sys_mod = PyImport_ImportModule("sys");
    if (!sys_mod) {
        return -1;
    }
    // Get sys.prefix string
    PyObject *prefix_obj = PyObject_GetAttrString(sys_mod, "prefix");
    if (!prefix_obj) {
        Py_DECREF(sys_mod);
        return -1;
    }
    const char *prefix_c = PyUnicode_AsUTF8(prefix_obj);
    if (!prefix_c) {
        Py_DECREF(sys_mod);
        Py_DECREF(prefix_obj);
        return -1;
    }
    // Duplicate prefix string for storage
    sys_prefix_str = strdup(prefix_c);
    Py_DECREF(prefix_obj);
    if (!sys_prefix_str) {
        Py_DECREF(sys_mod);
        PyErr_NoMemory();
        return -1;
    }
    // Retrieve sys._current_frames function
    PyObject *current_frames = PyObject_GetAttrString(sys_mod, "_current_frames");
    Py_DECREF(sys_mod);
    if (!current_frames || !PyCallable_Check(current_frames)) {
        Py_XDECREF(current_frames);
        PyErr_SetString(PyExc_RuntimeError, "sys._current_frames not callable");
        return -1;
    }
    current_frames_func = current_frames; // steal reference
    // Import site module and fetch site.getsitepackages() list
    PyObject *site_mod = PyImport_ImportModule("site");
    if (!site_mod) {
        return -1;
    }
    PyObject *getsitepackages = PyObject_GetAttrString(site_mod, "getsitepackages");
    if (!getsitepackages || !PyCallable_Check(getsitepackages)) {
        Py_XDECREF(getsitepackages);
        Py_DECREF(site_mod);
        PyErr_SetString(PyExc_RuntimeError, "site.getsitepackages not callable");
        return -1;
    }
    PyObject *site_list = PyObject_CallObject(getsitepackages, NULL);
    Py_DECREF(getsitepackages);
    Py_DECREF(site_mod);
    if (!site_list || !PySequence_Check(site_list)) {
        Py_XDECREF(site_list);
        PyErr_SetString(PyExc_RuntimeError, "site.getsitepackages returned non-sequence");
        return -1;
    }
    Py_ssize_t n = PySequence_Size(site_list);
    num_site_packages = (int)n;
    if (num_site_packages > 0) {
        site_packages_paths = (char **)calloc(num_site_packages, sizeof(char *));
        if (!site_packages_paths) {
            Py_DECREF(site_list);
            PyErr_NoMemory();
            return -1;
        }
        for (int i = 0; i < num_site_packages; i++) {
            PyObject *item = PySequence_GetItem(site_list, i);
            if (!item) {
                Py_DECREF(site_list);
                return -1;
            }
            const char *path_c = PyUnicode_AsUTF8(item);
            if (path_c) {
                site_packages_paths[i] = strdup(path_c);
                if (!site_packages_paths[i]) {
                    Py_DECREF(item);
                    Py_DECREF(site_list);
                    PyErr_NoMemory();
                    return -1;
                }
            }
            Py_DECREF(item);
        }
    }
    Py_DECREF(site_list);
    paths_initialized = 1;
    return 0;
}

// Set the application base directory prefix used for categorising
// Python frames.  This function accepts a single string argument and
// stores an internal copy of the string.  Passing None resets the
// application prefix to NULL.  The caller must hold the GIL.
static PyObject *clinic_set_app_base(PyObject *self, PyObject *args) {
    const char *path = NULL;
    if (!PyArg_ParseTuple(args, "|z", &path)) {
        return NULL;
    }
    // Free any existing prefix
    free(app_base_path);
    app_base_path = NULL;
    if (path && path[0] != '\0') {
        app_base_path = strdup(path);
        if (!app_base_path) {
            return PyErr_NoMemory();
        }
    }
    Py_RETURN_NONE;
}

#ifdef __unix__
// Sampling thread function.  This function runs in a loop until
// ``monitoring`` is cleared.  It writes binary records when a
// filepath is provided.  When no filepath is specified it falls
// back to writing CSV lines to stdout.
static void *sampling_loop(void *arg) {
    // Write binary header to the metrics file.  No CSV fallback
    // exists because metrics are always written in binary format.
    if (metrics_fp) {
        FileHeader hdr;
        memset(&hdr, 0, sizeof(hdr));
        memcpy(hdr.magic, "CLINICPY", 8);
        hdr.version = 2;
        fwrite(&hdr, sizeof(hdr), 1, metrics_fp);
        fflush(metrics_fp);
    }
    start_time = now_monotonic();
    // Sample every 50 ms by default.
    const long interval_ns = 50L * 1000000L;
    struct timespec next;
    clock_gettime(CLOCK_MONOTONIC, &next);
    while (monitoring) {
        // Acquire resource usage.  RUSAGE_SELF reports the process as a whole.
        struct rusage ru;
        if (getrusage(RUSAGE_SELF, &ru) == 0) {
            double ts = now_monotonic() - start_time;
            double utime = ru.ru_utime.tv_sec + ru.ru_utime.tv_usec / 1e6;
            double stime = ru.ru_stime.tv_sec + ru.ru_stime.tv_usec / 1e6;
            long rss_kb = ru.ru_maxrss;
            long inb = ru.ru_inblock;
            long outb = ru.ru_oublock;
            long nv = ru.ru_nvcsw;
            long niv = ru.ru_nivcsw;
            // Initialise Python path data on first sample after start.
            // Note: we do not call init_python_paths() at module
            // import time because it requires the GIL.  Instead we
            // perform lazy initialization here once the sampling thread
            // runs.  When metrics_fp is non-null we are guaranteed
            // that clinic_start() was called from a Python thread and
            // therefore the interpreter is initialised.  Acquire the
            // GIL only if Python objects are needed.
            long py_app_count = 0;
            long py_lib_count = 0;
            long py_core_count = 0;
            if (current_frames_func) {
                // Acquire GIL to call Python API.  Because the sampling
                // thread is detached we must guard all Python calls.
                PyGILState_STATE gstate = PyGILState_Ensure();
                if (!paths_initialized) {
                    // initialise path prefixes if not yet done.  If
                    // initialization fails we swallow the exception
                    // here because exceptions cannot propagate into
                    // sampling loop; instead frames will be counted as
                    // core frames by default.
                    if (init_python_paths() != 0) {
                        PyErr_Clear();
                    }
                }
                // Retrieve dictionary of thread frame objects.
                // Use a simpler approach that's less likely to crash
                PyObject *frames_dict = NULL;
                if (PyErr_Occurred()) {
                    PyErr_Clear();
                }
                frames_dict = PyObject_CallObject(current_frames_func, NULL);
                if (frames_dict && PyDict_Check(frames_dict)) {
                    // Iterate through values of frames_dict
                    PyObject *values = PyDict_Values(frames_dict);
                    if (values) {
                        Py_ssize_t num_threads = PyList_Size(values);
                        for (Py_ssize_t t = 0; t < num_threads; t++) {
                            PyObject *frame_obj = PyList_GetItem(values, t);
                            if (!frame_obj) continue;
                            
                            // Traverse frame chain with safety limits
                            PyObject *cur = frame_obj;
                            Py_INCREF(cur);
                            int depth = 0;
                            const int MAX_DEPTH = 100; // Prevent infinite loops
                            
                            while (cur && cur != Py_None && depth < MAX_DEPTH) {
                                // Try to get f_code safely
                                PyObject *code = PyObject_GetAttrString(cur, "f_code");
                                if (!code) {
                                    PyErr_Clear();
                                    break;
                                }
                                PyObject *filename_obj = PyObject_GetAttrString(code, "co_filename");
                                Py_DECREF(code);
                                if (!filename_obj) {
                                    PyErr_Clear();
                                    break;
                                }
                                const char *fname = PyUnicode_AsUTF8(filename_obj);
                                if (fname) {
                                    // Categorise based on path prefixes
                                    int classified = 0;
                                    if (app_base_path && fname[0] != '\0') {
                                        size_t app_len = strlen(app_base_path);
                                        if (app_len > 0 && strncmp(fname, app_base_path, app_len) == 0) {
                                            py_app_count++;
                                            classified = 1;
                                        }
                                    }
                                    if (!classified && num_site_packages > 0) {
                                        for (int i = 0; i < num_site_packages; i++) {
                                            if (site_packages_paths[i]) {
                                                const char *pkg = site_packages_paths[i];
                                                size_t pkg_len = strlen(pkg);
                                                if (pkg_len > 0 && strncmp(fname, pkg, pkg_len) == 0) {
                                                    py_lib_count++;
                                                    classified = 1;
                                                    break;
                                                }
                                            }
                                        }
                                    }
                                    if (!classified && sys_prefix_str) {
                                        size_t pre_len = strlen(sys_prefix_str);
                                        if (pre_len > 0 && strncmp(fname, sys_prefix_str, pre_len) == 0) {
                                            py_core_count++;
                                            classified = 1;
                                        }
                                    }
                                    if (!classified) {
                                        py_core_count++;
                                    }
                                }
                                Py_DECREF(filename_obj);
                                
                                // Move to f_back safely
                                PyObject *back = PyObject_GetAttrString(cur, "f_back");
                                Py_DECREF(cur);
                                cur = back;
                                depth++;
                                
                                // Clear any errors that might have occurred
                                if (PyErr_Occurred()) {
                                    PyErr_Clear();
                                    break;
                                }
                            }
                            Py_XDECREF(cur);
                        }
                        Py_DECREF(values);
                    }
                    Py_DECREF(frames_dict);
                } else {
                    Py_XDECREF(frames_dict);
                    PyErr_Clear();
                }
                PyGILState_Release(gstate);
            }
            if (metrics_fp) {
                MetricRecord rec;
                rec.timestamp = ts;
                rec.user_time = utime;
                rec.system_time = stime;
                rec.rss_kb = rss_kb;
                rec.inblock = inb;
                rec.oublock = outb;
                rec.nvcsw = nv;
                rec.nivcsw = niv;
                rec.py_app_frames = py_app_count;
                rec.py_lib_frames = py_lib_count;
                rec.py_core_frames = py_core_count;
                fwrite(&rec, sizeof(rec), 1, metrics_fp);
                fflush(metrics_fp);
            }
        }
        // Sleep until next period.
        next.tv_nsec += interval_ns;
        next.tv_sec += next.tv_nsec / 1000000000L;
        next.tv_nsec %= 1000000000L;
        struct timespec now;
        clock_gettime(CLOCK_MONOTONIC, &now);
        // Compute time difference.
        long diff_sec = next.tv_sec - now.tv_sec;
        long diff_ns = next.tv_nsec - now.tv_nsec;
        if (diff_ns < 0) {
            diff_ns += 1000000000L;
            diff_sec -= 1;
        }
        if (diff_sec >= 0) {
            struct timespec sleep_ts = { diff_sec, diff_ns };
            nanosleep(&sleep_ts, NULL);
        }
    }
    return NULL;
}
#endif

// Start the sampling thread.  If a filename is provided, metrics will
// be written in binary format to that file.  Otherwise metrics are
// printed as CSV to stdout.
static PyObject *clinic_start(PyObject *self, PyObject *args, PyObject *kwds) {
    static char *keywords[] = { "filepath", NULL };
    const char *filepath = NULL;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|s", keywords, &filepath)) {
        return NULL;
    }
    if (monitoring) {
        Py_RETURN_NONE;
    }
    // Open output file if requested.  Always write binary metrics.  If
    // no filepath is provided, use a default filename "metrics.bin"
    const char *path_to_use = filepath;
    static const char default_file[] = "metrics.bin";
    if (!path_to_use || path_to_use[0] == '\0') {
        path_to_use = default_file;
    }
    metrics_fp = fopen(path_to_use, "wb");
    if (!metrics_fp) {
        PyErr_Format(PyExc_OSError, "Could not open %s for writing", path_to_use);
        return NULL;
    }
#ifdef __unix__
    // Initialise Python paths before starting the sampling thread.  If
    // this fails we abort start() to avoid running with incomplete
    // configuration.  Acquire the GIL explicitly because start()
    // executes while holding the GIL from Python.
    if (init_python_paths() != 0) {
        // init_python_paths sets a Python exception on failure
        if (metrics_fp) {
            fclose(metrics_fp);
            metrics_fp = NULL;
        }
        return NULL;
    }
#endif
#ifdef __unix__
    monitoring = 1;
    int err = pthread_create(&monitor_thread, NULL, sampling_loop, NULL);
    if (err != 0) {
        monitoring = 0;
        if (metrics_fp) {
            fclose(metrics_fp);
            metrics_fp = NULL;
        }
        PyErr_Format(PyExc_RuntimeError, "Failed to create monitor thread: %s",
                     strerror(err));
        return NULL;
    }
    pthread_detach(monitor_thread);
#else
    // Unsupported platform: simply set monitoring flag to skip repeated starts.
    monitoring = 1;
    fprintf(stderr, "clinic_monitor: resource sampling not supported on this platform\n");
#endif
    Py_RETURN_NONE;
}

// Stop the sampling thread.  Closes the output file if necessary.
static PyObject *clinic_stop(PyObject *self, PyObject *args) {
    if (!monitoring) {
        Py_RETURN_NONE;
    }
    monitoring = 0;
#ifdef __unix__
    // Wait briefly to allow the thread to exit.  Not strictly necessary
    // because pthread_detach has been called, but ensures that the last
    // sample is flushed.
    struct timespec ts = {0, 10000000L}; // 10 ms
    nanosleep(&ts, NULL);
#endif
    if (metrics_fp) {
        fclose(metrics_fp);
        metrics_fp = NULL;
    }
    Py_RETURN_NONE;
}

static PyMethodDef ClinicMethods[] = {
    {"start", (PyCFunction)clinic_start, METH_VARARGS | METH_KEYWORDS,
     "start(filepath=None) -> None\n\n"
     "Start collecting resource usage samples.  Metrics are always\n"
     "written as binary records to a file.  If 'filepath' is None,\n"
     "a default file named 'metrics.bin' is created in the current\n"
     "working directory.  Each record includes aggregated Python\n"
     "frame counts in addition to process metrics."},
    {"stop", clinic_stop, METH_NOARGS,
     "stop() -> None\n\n"
     "Stop collecting resource usage samples and close the output file."},
    {"set_app_base", (PyCFunction)clinic_set_app_base, METH_VARARGS,
     "set_app_base(path: Optional[str]) -> None\n\n"
     "Set the directory prefix that identifies your application code.\n"
     "Frames whose filename begins with this prefix are counted as\n"
     "application frames in the aggregated statistics.  Passing None\n"
     "clears the prefix."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef clinic_module = {
    PyModuleDef_HEAD_INIT,
    "clinic_monitor",
    "Resource usage sampler for clinic_py",
    -1,
    ClinicMethods
};

PyMODINIT_FUNC
PyInit_clinic_monitor(void) {
    return PyModule_Create(&clinic_module);
}