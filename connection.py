from PySide import QtCore, QtGui

import name
import colors

_colors = {
        name.Name:  colors.yellow,
        float:      colors.blue
}

class Connection(object):
    """ Represents a connection between two datums.
        The target datum tracks the source datum's value.
    """
    def __init__(self, datum):
        self.source = datum
        self.source.outputs.append(self)
        self.target = None
        self.control = None

    def can_connect_to(self, datum):
        """ Returns True if we can connect to the given datum.
        """
        return (datum != self.source and
                self.source.type == datum.type and
                datum.inputs == [])


    def connect_to(self, target):
        self.target = target
        self.target.inputs.append(self)

    def disconnect_from_target(self):
        self.target.inputs.remove(self)
        self.target = None

    def disconnect_from_source(self):
        self.source.outputs.remove(self)
        self.source = None



class ConnectionControl(QtGui.QWidget):
    """ GUI wrapper around a connection.
    """
    def __init__(self, connection, parent):
        super(ConnectionControl, self).__init__(parent)
        self.connection = connection
        connection.control = self

        self.resize(10, 10)

        origin = self.get_origin()
        self.drag_pos = self.get_origin()
        self.hovering_over = None
        self.sync()

        self.show()

    def sync(self):
        """ Positions this connection appropriately, hides based on
            whether we should draw this connection, and re-renders
            mask if geometry has changed.
        """
        origin, target = self.get_origin(), self.get_target()

        # If we don't have a node to which we should connect,
        # then hide this widget and return.
        if origin is None or target is None:
            self.hide()
            return
        # Otherwise, show and raise the widget.
        elif self.isHidden():
            self.show()
            self.raise_()

        xmin = min(origin.x(), target.x()) - 5
        ymin = min(origin.y(), target.y()) - 5

        newGeom = QtCore.QRect(xmin, ymin,
                max(origin.x(), target.x()) + 5 - xmin,
                max(origin.y(), target.y()) + 5 - ymin)

        if newGeom != self.geometry():
            self.setGeometry(newGeom)
            self.make_mask()


    def make_mask(self):
        """ Updates the widget mask.
        """
        painter = QtGui.QPainter()
        bitmap = QtGui.QBitmap(self.size())
        bitmap.clear()

        painter.begin(bitmap)
        self.paint(painter, mask=True)
        painter.end()

        self.setMask(bitmap)


    def dragTo(self, pos):
        """ Sets the drag endpoint to the given position
            (in canvas coordinates).
        """
        self.drag_pos = pos
        hit = self.parentWidget().find_input(self.drag_pos)
        if hit is not None and not self.connection.can_connect_to(hit.datum):
            hit = False

        if self.hovering_over:
            # Turn off hover highlight if we've moved off this point
            if not hit:
                self.hovering_over.hovering = False
                self.hovering_over.update()
        else:
            # Turn on hover highlight if we've moved onto this point.
            if hit:
                hit.hovering = True
                hit.update()

        self.hovering_over = hit

        self.sync()

    def release(self):
        """ Attempts to connect this widget to an Input widget.
            Calls deleteLater if not successful.
        """
        if not self.hovering_over:
            self.connection.disconnect_from_source()
            self.hide()
            self.deleteLater()
        else:
            self.connection.connect_to(self.hovering_over.datum)
            self.hovering_over.hovering = False
            self.sync()


    def paintEvent(self, paintEvent):
        if self.isHidden():     return
        self.paint(QtGui.QPainter(self))

    def paint(self, painter, mask=False):
        origin, target = self.get_origin(), self.get_target()

        if mask:
            color = QtCore.Qt.color1
        elif self.hovering_over is not False:
            color = QtGui.QColor(
                    *_colors.get(self.connection.source.type, colors.red))
        else:
            color = QtGui.QColor(*colors.red)

        painter.setPen(QtGui.QPen(color, 4))
        painter.drawLine(origin - self.pos(), target - self.pos())

    def get_origin(self):
        """ Returns a canvas pixel location for the connected io.Output object.
            If no such object exists, returns None.
        """
        control = self.connection.source.node.control
        return control.get_datum_output(self.connection.source)


    def get_target(self):
        """ Returns a canvas pixel location for the connected io.Input object.
            If we aren't yet connected, return the mouse drag position.
            If we are connected but no target position exists, return None
        """
        if not self.connection.target:  return self.drag_pos
        control = self.connection.target.node.control
        return control.get_datum_input(self.connection.target)

################################################################################

class IO(QtGui.QWidget):
    def __init__(self, datum, parent):
        super(IO, self).__init__(parent)
        self.setFixedSize(10, 10)

        self.datum = datum
        self.color = _colors.get(self.datum.type, colors.red)
        self.hovering = False

    def paintEvent(self, paintEvent):
        painter = QtGui.QPainter(self)
        if self.hovering:   color = (min(255, c + 60) for c in self.color)
        else:               color = self.color
        painter.setBackground(QtGui.QColor(*color))
        painter.eraseRect(self.rect())


class Input(IO):
    def __init__(self, datum, parent):
        super(Input, self).__init__(datum, parent)

    def mouse_hit(self, pos):
        """ Returns true if the given position (in canvas coordinates)
            is within this widget.
        """
        return self.geometry().contains(pos - self.parentWidget().pos())


class Output(IO):
    def __init__(self, datum, parent):
        super(Output, self).__init__(datum, parent)
        self.connection = None

    def enterEvent(self, event):
        self.hovering = True
        self.update()

    def leaveEvent(self, event):
        self.hovering = False
        self.update()

    def mouseMoveEvent(self, event):
        if self.connection:
            self.connection.dragTo(
                    event.pos() + self.pos() + self.parentWidget().pos())

    def mouseReleaseEvent(self, event):
        if self.connection:
            self.connection.dragTo(
                    event.pos() + self.pos() + self.parentWidget().pos())
            self.connection.release()
            self.connection = None

    def mousePressEvent(self, event):
        self.connection = ConnectionControl(
                Connection(self.datum),
                self.parentWidget().parentWidget())

