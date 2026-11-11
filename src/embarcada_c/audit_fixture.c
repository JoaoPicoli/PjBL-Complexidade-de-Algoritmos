/* Positive control for instrumentation only; never linked into dedup.dll. */
#include "dedup.h"
#include <stdlib.h>
PJBL_API void *pjbl_allocation_fixture(void) { return malloc(17); }
