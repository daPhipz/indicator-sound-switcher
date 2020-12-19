#!/bin/sh

if [ ! -d "$SNAP_USER_DATA/.config/autostart" ]; then
	mkdir -p $SNAP_USER_DATA/.config/autostart
	ln -sfnt $SNAP_USER_DATA/.config/autostart/ $SNAP/meta/gui/indicator-sound-switcher.desktop
fi

exec "$@"
