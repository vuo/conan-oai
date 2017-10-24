#include <stdio.h>
#include <assimp/cimport.h>

int main()
{
    printf("%ld import formats available.\n", aiGetImportFormatCount());
	return 0;
}
