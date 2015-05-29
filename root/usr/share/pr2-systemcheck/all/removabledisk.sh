#!/bin/sh

if [ ! -e /dev/removable ]; then
    echo "/dev/removable does not exist.  This is only ok if there is no drive in the removable bay." >&2
    exit 1
fi

if [ ! -e /dev/removable1 ]; then
    echo "/dev/removable1 does not exist.  The drive is probably not formatted." >&2
    exit 1
fi

realname=`readlink -f /dev/removable1`
mounted=`grep -c "${realname} /removable" /etc/mtab`

if [ ${mounted} -eq 0 ]; then
    mount /removable || {
	echo "Could not mount /dev/removable1" >&2
	exit 2
    }
fi

perms=`ls -ld /removable/ | awk '{print $1}'`
group=`ls -ld /removable/ | awk '{print $4}'`

res=0

if [ ! "${perms}" = "drwxrwxr-x" ]; then
    echo "/removable has incorrect permissions" >&2
    echo "  to fix: mount /removable; sudo chmod 775 /removable" >&2
    res=3
fi

if [ ! "${group}" = "users" ]; then
    echo "/removable not set to 'users' group" >&2
    echo "  to fix: mount /removable; sudo chown root.users /removable" >&2
    res=3
fi

if [ ${mounted} -eq 0 ]; then
    umount /removable || {
	echo "Could not unmount /dev/removable1" >&2
	exit 4
    }
fi

exit ${res}