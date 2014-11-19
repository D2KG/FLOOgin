# -*- coding: utf-8 -*-
"""
/***************************************************************************
 floogin
                                 A QGIS plugin
 Flood Disaster Management
                             -------------------
        begin                : 2014-05-03
        copyright            : (C) 2014 by FLOOgin group
        email                : kasun.ramanayake@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    # load floogin class from file floogin
    from floogin import floogin
    return floogin(iface)
