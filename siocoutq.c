#include <sys/ioctl.h> /* ioctl() */
#include <linux/sockios.h> /* SIOCOUTQ */
#include <stdio.h>

int
main(int argc, char **argv)
{
    printf("SIOCOUTQ: 0x%08x\n", SIOCOUTQ);
}
