/* Audit apparatus, compiled separately from the algorithm object.
 * Counters are not production algorithm storage. Any allocation requested
 * by the instrumented algorithm is counted and refused (fail closed). */
#include "dedup.h"

static size_t calls;
static size_t requested;

PJBL_API void pjbl_alloc_reset(void) { calls = 0; requested = 0; }
PJBL_API size_t pjbl_alloc_calls(void) { return calls; }
PJBL_API size_t pjbl_alloc_requested(void) { return requested; }
void *pjbl_malloc(size_t n) { ++calls; requested += n; return NULL; }
void *pjbl_calloc(size_t n, size_t s) { ++calls; requested += n * s; return NULL; }
void *pjbl_realloc(void *p, size_t n) { (void)p; ++calls; requested += n; return NULL; }
void pjbl_free(void *p) { (void)p; ++calls; }
