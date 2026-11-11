#include "dedup.h"

_Static_assert(sizeof(uint16_t) == 2, "16-bit readings are required");
_Static_assert(SIZE_MAX >= 10000000, "size_t must index all required inputs");

size_t dedup_heapsort_u16(uint16_t *a, size_t n)
{
    size_t start, end, root, child, read, write;
    uint16_t key;

    if (n < 2) {
        return n;
    }
    start = n / 2;
    end = n;
    /* First build a max-heap, then extract its maximum into the suffix.
     * Combining both phases keeps all work in a single leaf function. */
    for (;;) {
        if (start != 0) {
            --start;
            key = a[start];
        } else {
            --end;
            if (end == 0) {
                break;
            }
            key = a[end];
            a[end] = a[0];
        }
        root = start;
        while (root < end / 2) {
            child = 2 * root + 1;
            if (child + 1 < end && a[child] < a[child + 1]) {
                ++child;
            }
            if (key >= a[child]) {
                break;
            }
            a[root] = a[child];
            root = child;
        }
        a[root] = key;
    }
    write = 1;
    for (read = 1; read < n; ++read) {
        if (a[read] != a[write - 1]) {
            a[write] = a[read];
            ++write;
        }
    }
    return write;
}
