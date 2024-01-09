from tkinter import *

from . import Global

DEBUG3D = 0


# ________________________________________
class Canvas3D(Canvas):
    def __transform3D(self, pts):
        ORIGIN = self.ORIGIN
        SCREEN_Z = self.SCREEN_Z
        newpts = []
        for i in range(0, len(pts), 3):
            nx = pts[i]
            ny = pts[i + 1]
            nz = pts[i + 2]
            newpts.append(ORIGIN + (nx * SCREEN_Z // nz))
            newpts.append(ORIGIN - (ny * SCREEN_Z // nz))
        return newpts

    def cls(self):
        for i in self.find_all():
            self.delete(i)

    def drawBlock3D(self, nx, ny, fill, outline, altitude=-1, height=2, stipple=None):
        # This is *2 so I don't have to use floats to center the tiles:
        # -1 0 +1     -1 0 +1
        # +-----+-----+-----+ +1
        # |     |     |     |
        # |  +  |  +  |  +  |  0
        # |     |     |     |
        # +-----+-----+-----+ -1
        #       -1 0 +1
        nx0 = nx * 2 - 1
        nx1 = nx * 2 + 1
        ny0 = altitude
        ny1 = height + altitude
        nz0 = ny * 2 + 1
        nz1 = ny * 2 + 3
        if nx < 0:
            pts = [
                nx0,
                ny0,
                nz0,
                nx1,
                ny0,
                nz0,
                nx1,
                ny0,
                nz1,
                nx1,
                ny1,
                nz1,
                nx1,
                ny1,
                nz0,
                nx0,
                ny1,
                nz0,
            ]
        elif nx > 0:
            pts = [
                nx0,
                ny0,
                nz0,
                nx1,
                ny0,
                nz0,
                nx1,
                ny1,
                nz0,
                nx0,
                ny1,
                nz0,
                nx0,
                ny1,
                nz1,
                nx0,
                ny0,
                nz1,
            ]
        else:
            pts = [
                nx0,
                ny0,
                nz0,
                nx1,
                ny0,
                nz0,
                nx1,
                ny1,
                nz0,
                nx0,
                ny1,
                nz0,
            ]
        pts = self.__transform3D(pts)
        if DEBUG3D:
            print("drawBlock3D %s" % pts)
        if len(pts) == 8:
            # I know that all 4-point polys in drawBlock3D are rectangular...
            self.create_rectangle(
                pts[0],
                pts[1],
                pts[4],
                pts[5],
                fill=fill,
                outline=outline,
            )
        else:
            self.create_polygon(pts, fill=fill, outline=outline, stipple=stipple)

    def drawPanel3D(
        self,
        side,
        nx,
        ny,
        fill,
        outline,
        altitude=-1,
        height=2,
        stipple=None,
    ):
        # don't draw things that should be behind you!
        if side == Global.Side_Near and nx == ny == 0:
            return
        nx0 = nx * 2 - 1
        nx1 = nx * 2 + 1
        ny0 = altitude
        ny1 = height + altitude
        nz0 = ny * 2 + 1
        nz1 = ny * 2 + 3
        if side == Global.Side_Top:
            pts = [
                nx0,
                ny1,
                nz0,
                nx1,
                ny1,
                nz0,
                nx1,
                ny1,
                nz1,
                nx0,
                ny1,
                nz1,
            ]
        elif side == Global.Side_Bottom:
            pts = [
                nx0,
                ny0,
                nz0,
                nx1,
                ny0,
                nz0,
                nx1,
                ny0,
                nz1,
                nx0,
                ny0,
                nz1,
            ]
        elif side == Global.Side_Left:
            pts = [
                nx0,
                ny0,
                nz0,
                nx0,
                ny0,
                nz1,
                nx0,
                ny1,
                nz1,
                nx0,
                ny1,
                nz0,
            ]
        elif side == Global.Side_Right:
            pts = [
                nx1,
                ny0,
                nz0,
                nx1,
                ny0,
                nz1,
                nx1,
                ny1,
                nz1,
                nx1,
                ny1,
                nz0,
            ]
        elif side == Global.Side_Near:
            pts = [
                nx0,
                ny0,
                nz0,
                nx1,
                ny0,
                nz0,
                nx1,
                ny1,
                nz0,
                nx0,
                ny1,
                nz0,
            ]
            self.drawRectangle3D(pts, fill, outline, stipple=stipple)
            return
        elif side == Global.Side_Far:
            pts = [
                nx0,
                ny0,
                nz1,
                nx1,
                ny0,
                nz1,
                nx1,
                ny1,
                nz1,
                nx0,
                ny1,
                nz1,
            ]
            self.drawRectangle3D(pts, fill, outline, stipple=stipple)
            return
        else:
            assert 0, "Unknown panel side %s" % side
        self.drawPolygon3D(pts, fill, outline, stipple=stipple)

    def drawFloor3D(self, nx, ny, fill, outline, stipple=None):
        nx0 = nx * 2 - 1
        nx1 = nx * 2 + 1
        ny0 = -1
        nz0 = ny * 2 + 1
        nz1 = ny * 2 + 3
        pts = [
            nx0,
            ny0,
            nz0,
            nx1,
            ny0,
            nz0,
            nx1,
            ny0,
            nz1,
            nx0,
            ny0,
            nz1,
        ]
        self.drawPolygon3D(pts, fill, outline, stipple=stipple)

    def drawLine3D(self, pts, fill, width=1, stipple=None):
        pts = self.__transform3D(pts)
        if DEBUG3D:
            print("drawLine %s" % pts)
        self.create_line(pts, fill=fill, width=width, stipple=stipple)

    def drawOval3D(self, pts, fill, outline, stipple=None):
        pts = self.__transform3D(pts)
        if DEBUG3D:
            print("drawOval3D %s" % pts)
        self.create_oval(
            pts[0],
            pts[1],
            pts[2],
            pts[3],
            fill=fill,
            outline=outline,
            stipple=stipple,
        )

    def drawPolygon3D(self, pts, fill, outline, stipple=None):
        pts = self.__transform3D(pts)
        if DEBUG3D:
            print("drawPolygon3D %s" % pts)
        self.create_polygon(pts, fill=fill, outline=outline, stipple=stipple)

    def drawRectangle3D(self, pts, fill, outline, stipple=None):
        pts = self.__transform3D(pts)
        if DEBUG3D:
            print("drawRectangle3D %s" % pts)
        self.create_rectangle(
            pts[0],
            pts[1],
            pts[4],
            pts[5],
            fill=fill,
            outline=outline,
            stipple=stipple,
        )

    def drawText3D(self, x, y, z, text, fill):
        pts = self.__transform3D([x, y, z])
        if DEBUG3D:
            print("drawText3D %s '%s'" % (pts, text))
        fontsize = self.font3dsize // z
        self.create_text(
            pts[0],
            pts[1],
            text=text,
            font=("Times", fontsize),
            fill=fill,
            anchor=S,
        )
