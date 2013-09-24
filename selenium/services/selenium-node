#!/bin/bash
#
#       /etc/rc.d/init.d/
#
#

# Source function library.
. /etc/init.d/functions

RETVAL=0
PROCNAME=selenium-node-1
exec="/opt/selenium-server/selenium-node-1/start-selenium-node.sh"
pidfile="/opt/selenium-server/selenium-node-1/selenium-node.pid"
logfile="/opt/selenium-server/selenium-node-1/log/selenium-node.log"

start() {
    if [ ! -f $pidfile ]; then
	    touch "$pidfile"
    else
	if [ -r $pidfile ]; then
		pid=`cat "$pidfile"`
		ps -p $pid >/dev/null 2>&1
		if [ $? -eq 0 ]; then
			echo "Selenium node $PROCNAME appears to still be running with PID $pid. Start aborted."
			exit 1
		else
			echo "Removing/clearing stale PID file. "
			rm -f "$pidfile" >/dev/null 2>&1
			if [ $? != 0 ]; then
				if [ -w "$pidfile" ]; then
					cat /dev/null >"$pidfile"
				else
					echo "Unable to remove or clear stale PID file. Start aborted."
					exit 1
				fi
			fi
		fi
	else
		echo "Unable to read PID file. Start aborted."
		exit 1
	fi
    fi

    echo -n "Starting Selenium node: $PROCNAME"
    $exec >>"$logfile" 2>&1 &

    RETVAL=$?
    pid=$!

	if [ $RETVAL -eq 0 ]
	then
		echo_success
 		echo $pid >"$pidfile"
	else
		echo_failure
	fi

	echo
}

stop() {
    if [ ! -f $pidfile ]; then
	    echo "PID file $pidfile does not exist"
	    exit 1
    fi
    if [ -r $pidfile ]; then
	    pid=`cat "$pidfile"`

        ps -p $pid >/dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo -n "Shutting down selenium node: $PROCNAME"
            kill $pid
            RETVAL=$?

            SLEEP=10
            while [[ $SLEEP -gt 0 ]]; do
                kill -0 $pid >/dev/null 2>&1
                if [ $? -gt 0 ]; then
                    echo_success
                    echo

                    rm -f "$pidfile" >/dev/null 2>&1
                    if [ $? != 0 ]; then
                        if [ -w "$pidfile" ]; then
                            cat /dev/null > "$pidfile"
                        else
                            echo "Selenium node $PROCNAME stopped but the PID file could not be removed or cleared."
                        fi
                    fi
                    break
                else
                    if [ $SLEEP -gt 0 ]; then
                        sleep 1
                    fi
                    if [ $SLEEP -eq 0 ]; then
                        echo_failure
                    fi
                    SLEEP=`expr $SLEEP - 1 `
                fi
            done
        else
            echo "Selenium node $PROCNAME with PID $PID is not running. "

            rm -f "$pidfile" >"$logfile" 2>&1
            if [ $? != 0 ]; then
                if [ -w "$pidfile" ]; then
                cat /dev/null > "$pidfile"
                else
                echo "Unable to remove or clear stale PID file. Stop aborted."
                exit 1
                fi
            fi
            fi
        else
        echo "Unable to read PID file. Stop aborted."
        exit 1
        fi

    echo
}

status() {
	echo
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    status)

        ;;
    restart)
        stop
        start
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        RETVAL=2
        ;;
esac
exit $RETVAL
