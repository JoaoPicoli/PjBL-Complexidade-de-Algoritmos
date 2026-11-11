#ifndef PJBL_DEDUP_H
#define PJBL_DEDUP_H

#include <stddef.h>
#include <stdint.h>

#ifdef _WIN32
#define PJBL_API __declspec(dllexport)
#else
#define PJBL_API
#endif

/* a has n resident uint16_t elements. NULL is allowed only when n == 0.
 * Returns d; a[0:d] is the strictly increasing set of input values.
 * No allocation, recursion or writable static storage. */
PJBL_API size_t dedup_heapsort_u16(uint16_t *a, size_t n);

#endif
