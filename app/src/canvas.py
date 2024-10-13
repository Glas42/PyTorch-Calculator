from src.crashreport import CrashReport
import src.variables as variables
import traceback
import numpy
import cv2

LastContent = None
Frame = None

def Update():
    try:
        global LastContent
        global Frame

        Content = (len(variables.CANVAS_CONTENT),
                        variables.CANVAS_POSITION,
                        variables.CANVAS_ZOOM,
                        variables.CANVAS_SHOW_GRID,
                        variables.CANVAS_GRID_TYPE,
                        len(variables.CANVAS_TEMP),
                        len(variables.CANVAS_DELETE_LIST),
                        variables.TEXT_COLOR,
                        variables.TOOLBAR_HOVERED)

        if variables.PAGE == "Canvas" and LastContent != Content:
            if variables.CANVAS.shape != (variables.CANVAS_BOTTOM + 1, variables.WIDTH, 3):
                variables.CANVAS = numpy.zeros((variables.CANVAS_BOTTOM + 1, variables.WIDTH, 3), numpy.uint8)
                variables.CANVAS[:] = ((250, 250, 250) if variables.THEME == "Light" else (28, 28, 28))
            Frame = variables.CANVAS.copy()
            CANVAS_CONTENT = variables.CANVAS_CONTENT
            CANVAS_POSITION = variables.CANVAS_POSITION
            CANVAS_ZOOM = variables.CANVAS_ZOOM
            if variables.CANVAS_SHOW_GRID == True:
                grid_size = 50
                grid_width = round(Frame.shape[1] / (grid_size * CANVAS_ZOOM))
                grid_height = round(Frame.shape[0] / (grid_size * CANVAS_ZOOM))
                if CANVAS_ZOOM > 0.05:
                    if variables.CANVAS_GRID_TYPE == "LINE":
                        for X in range(0, grid_width):
                            PointX = round((X * grid_size + CANVAS_POSITION[0] / CANVAS_ZOOM % grid_size) * CANVAS_ZOOM)
                            cv2.line(Frame, (PointX, 0), (PointX, Frame.shape[0]), (127, 127, 127), 1, cv2.LINE_AA if variables.ANTI_ALIASING_LINES == True else cv2.LINE_8)
                        for Y in range(0, grid_height):
                            PointY = round((Y * grid_size + CANVAS_POSITION[1] / CANVAS_ZOOM % grid_size) * CANVAS_ZOOM)
                            cv2.line(Frame, (0, PointY), (Frame.shape[1], PointY), (127, 127, 127), 1, cv2.LINE_AA if variables.ANTI_ALIASING_LINES == True else cv2.LINE_8)
                    else:
                        for X in range(0, grid_width):
                            PointX = round((X * grid_size + CANVAS_POSITION[0] / CANVAS_ZOOM % grid_size) * CANVAS_ZOOM)
                            for Y in range(0, grid_height):
                                PointY = round((Y * grid_size + CANVAS_POSITION[1] / CANVAS_ZOOM % grid_size) * CANVAS_ZOOM)
                                cv2.circle(Frame, (PointX, PointY), 1, (127, 127, 127), -1, cv2.LINE_AA if variables.ANTI_ALIASING_LINES == True else cv2.LINE_8)

            LastPoint = None
            for X, Y in variables.CANVAS_TEMP:
                if LastPoint != None:
                    PointX1 = round((LastPoint[0] + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                    PointY1 = round((LastPoint[1] + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                    PointX2 = round((X + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                    PointY2 = round((Y + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                    if 0 <= PointX1 < Frame.shape[1] or 0 <= PointY1 < Frame.shape[0] or 0 <= PointX2 < Frame.shape[1] or 0 <= PointY2 < Frame.shape[0]:
                        cv2.line(Frame, (PointX1, PointY1), (PointX2, PointY2), variables.TEXT_COLOR, 3, cv2.LINE_AA if variables.ANTI_ALIASING_LINES == True else cv2.LINE_8)
                LastPoint = (X, Y)

            if len(variables.CANVAS_TEMP) == 1:
                PointX = round((variables.CANVAS_TEMP[0][0] + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                PointY = round((variables.CANVAS_TEMP[0][1] + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                if 0 <= PointX < Frame.shape[1] or 0 <= PointY < Frame.shape[0]:
                    cv2.circle(Frame, (PointX, PointY), 3, variables.TEXT_COLOR, -1, cv2.LINE_AA if variables.ANTI_ALIASING_LINES == True else cv2.LINE_8)
            for i in CANVAS_CONTENT:
                LastPoint = None
                MinX, MinY, MaxX, MaxY = i[0]
                MinX = round((MinX + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                MinY = round((MinY + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                MaxX = round((MaxX + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                MaxY = round((MaxY + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                if MaxX >= 0 and MinX < Frame.shape[1] and MaxY >= 0 and MinY < Frame.shape[0]:
                    if len(i[0]) == 4:
                        i = i[1:]
                    for X, Y in i:
                        if LastPoint != None:
                            PointX1 = round((LastPoint[0] + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                            PointY1 = round((LastPoint[1] + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                            PointX2 = round((X + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                            PointY2 = round((Y + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                            if 0 <= PointX1 < Frame.shape[1] or 0 <= PointY1 < Frame.shape[0] or 0 <= PointX2 < Frame.shape[1] or 0 <= PointY2 < Frame.shape[0]:
                                cv2.line(Frame, (PointX1, PointY1), (PointX2, PointY2), variables.TEXT_COLOR, 3, cv2.LINE_AA if variables.ANTI_ALIASING_LINES == True else cv2.LINE_8)
                        LastPoint = (X, Y)
                    if len(i) == 1:
                        PointX = round((i[0][0] + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                        PointY = round((i[0][1] + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                        if 0 <= PointX < Frame.shape[1] or 0 <= PointY < Frame.shape[0]:
                            cv2.circle(Frame, (PointX, PointY), 3, variables.TEXT_COLOR, -1, cv2.LINE_AA if variables.ANTI_ALIASING_LINES == True else cv2.LINE_8)

            if variables.TOOLBAR_HOVERED == True:
                cv2.rectangle(Frame, (Frame.shape[1] - variables.TOOLBAR_WIDTH -1, 20), (Frame.shape[1] - 21, variables.TOOLBAR_HEIGHT), (231, 231, 231) if variables.THEME == "Light" else (47, 47, 47), 20, cv2.LINE_AA)
                cv2.rectangle(Frame, (Frame.shape[1] - variables.TOOLBAR_WIDTH - 1, 20), (Frame.shape[1] - 21, variables.TOOLBAR_HEIGHT), (231, 231, 231) if variables.THEME == "Light" else (47, 47, 47), -1, cv2.LINE_AA)
                Frame[20:variables.TOOLBAR_HEIGHT, Frame.shape[1] - variables.TOOLBAR_WIDTH -1:Frame.shape[1] - 21] = cv2.resize(variables.TOOLBAR, (variables.TOOLBAR_WIDTH - 20, variables.TOOLBAR_HEIGHT - 20))

            variables.CANVAS_CHANGED = True
            LastContent = Content
    except:
        CrashReport("Canvas - Error in function Update.", str(traceback.format_exc()))