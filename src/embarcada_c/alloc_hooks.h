#ifndef PJBL_ALLOC_HOOKS_H
#define PJBL_ALLOC_HOOKS_H
#include <stdlib.h>
void *pjbl_malloc(size_t);
void *pjbl_calloc(size_t, size_t);
void *pjbl_realloc(void *, size_t);
void pjbl_free(void *);
#define malloc pjbl_malloc
#define calloc pjbl_calloc
#define realloc pjbl_realloc
#define free pjbl_free
#endif
