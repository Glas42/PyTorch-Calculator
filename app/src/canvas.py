from src.crashreport import CrashReport
import src.variables as variables
import traceback
import numpy
import cv2

LastContent = None
LastPage = None
Frame = None

def Update():
    try:
        global LastContent
        global LastPage
        global Frame

        if variables.PAGE != LastPage and False:
            if variables.PAGE == "Canvas":
                ui.tools.configure(image=ui.tools_icon)
                ui.tools.image = ui.tools_icon
            else:
                ui.tools.configure(image=ui.tools_placeholder)
                ui.tools.image = ui.tools_placeholder
        LastPage = variables.PAGE

        Content = (len(variables.CANVAS_CONTENT),
                        variables.CANVAS_POSITION,
                        variables.CANVAS_ZOOM,
                        variables.CANVAS_SHOW_GRID,
                        variables.CANVAS_GRID_TYPE,
                        len(variables.CANVAS_TEMP),
                        len(variables.CANVAS_DELETE_LIST),
                        variables.CANVAS_DRAW_COLOR,
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
                        for x in range(0, grid_width):
                            PointX = round((x * grid_size + CANVAS_POSITION[0] / CANVAS_ZOOM % grid_size) * CANVAS_ZOOM)
                            cv2.line(Frame, (PointX, 0), (PointX, Frame.shape[0]), (127, 127, 127), 1, cv2.LINE_AA if variables.ANTI_ALIASING_LINES == True else cv2.LINE_8)
                        for y in range(0, grid_height):
                            PointY = round((y * grid_size + CANVAS_POSITION[1] / CANVAS_ZOOM % grid_size) * CANVAS_ZOOM)
                            cv2.line(Frame, (0, PointY), (Frame.shape[1], PointY), (127, 127, 127), 1, cv2.LINE_AA if variables.ANTI_ALIASING_LINES == True else cv2.LINE_8)
                    else:
                        for x in range(0, grid_width):
                            PointX = round((x * grid_size + CANVAS_POSITION[0] / CANVAS_ZOOM % grid_size) * CANVAS_ZOOM)
                            for y in range(0, grid_height):
                                PointY = round((y * grid_size + CANVAS_POSITION[1] / CANVAS_ZOOM % grid_size) * CANVAS_ZOOM)
                                cv2.circle(Frame, (PointX, PointY), 1, (127, 127, 127), -1, cv2.LINE_AA if variables.ANTI_ALIASING_LINES == True else cv2.LINE_8)

            LastPoint = None
            for x, y in variables.CANVAS_TEMP:
                if LastPoint != None:
                    PointX1 = round((LastPoint[0] + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                    PointY1 = round((LastPoint[1] + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                    PointX2 = round((x + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                    PointY2 = round((y + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                    if 0 <= PointX1 < Frame.shape[1] or 0 <= PointY1 < Frame.shape[0] or 0 <= PointX2 < Frame.shape[1] or 0 <= PointY2 < Frame.shape[0]:
                        cv2.line(Frame, (PointX1, PointY1), (PointX2, PointY2), variables.CANVAS_DRAW_COLOR, 3, cv2.LINE_AA if variables.ANTI_ALIASING_LINES == True else cv2.LINE_8)
                LastPoint = (x, y)

            if len(variables.CANVAS_TEMP) == 1:
                PointX = round((variables.CANVAS_TEMP[0][0] + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                PointY = round((variables.CANVAS_TEMP[0][1] + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                if 0 <= PointX < Frame.shape[1] or 0 <= PointY < Frame.shape[0]:
                    cv2.circle(Frame, (PointX, PointY), 3, variables.CANVAS_DRAW_COLOR, -1, cv2.LINE_AA if variables.ANTI_ALIASING_LINES == True else cv2.LINE_8)
            for i in CANVAS_CONTENT:
                LastPoint = None
                minX, minY, maxX, maxY = i[0]
                minX = round((minX + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                minY = round((minY + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                maxX = round((maxX + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                maxY = round((maxY + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                if maxX >= 0 and minX < Frame.shape[1] and maxY >= 0 and minY < Frame.shape[0]:
                    if len(i[0]) == 4:
                        i = i[1:]
                    for x, y in i:
                        if LastPoint != None:
                            PointX1 = round((LastPoint[0] + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                            PointY1 = round((LastPoint[1] + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                            PointX2 = round((x + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                            PointY2 = round((y + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                            if 0 <= PointX1 < Frame.shape[1] or 0 <= PointY1 < Frame.shape[0] or 0 <= PointX2 < Frame.shape[1] or 0 <= PointY2 < Frame.shape[0]:
                                cv2.line(Frame, (PointX1, PointY1), (PointX2, PointY2), variables.CANVAS_DRAW_COLOR, 3, cv2.LINE_AA if variables.ANTI_ALIASING_LINES == True else cv2.LINE_8)
                        LastPoint = (x, y)
                    if len(i) == 1:
                        PointX = round((i[0][0] + CANVAS_POSITION[0] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                        PointY = round((i[0][1] + CANVAS_POSITION[1] * 1/CANVAS_ZOOM) * CANVAS_ZOOM)
                        if 0 <= PointX < Frame.shape[1] or 0 <= PointY < Frame.shape[0]:
                            cv2.circle(Frame, (PointX, PointY), 3, variables.CANVAS_DRAW_COLOR, -1, cv2.LINE_AA if variables.ANTI_ALIASING_LINES == True else cv2.LINE_8)

            if variables.TOOLBAR_HOVERED == True:
                cv2.rectangle(Frame, (Frame.shape[1] - variables.TOOLBAR_WIDTH -1, 20), (Frame.shape[1] - 21, variables.TOOLBAR_HEIGHT), (231, 231, 231) if variables.THEME == "Light" else (47, 47, 47), 20, cv2.LINE_AA)
                cv2.rectangle(Frame, (Frame.shape[1] - variables.TOOLBAR_WIDTH - 1, 20), (Frame.shape[1] - 21, variables.TOOLBAR_HEIGHT), (231, 231, 231) if variables.THEME == "Light" else (47, 47, 47), -1, cv2.LINE_AA)
                Frame[20:variables.TOOLBAR_HEIGHT, Frame.shape[1] - variables.TOOLBAR_WIDTH -1:Frame.shape[1] - 21] = cv2.resize(variables.TOOLBAR, (variables.TOOLBAR_WIDTH - 20, variables.TOOLBAR_HEIGHT - 20))

            variables.CANVAS_CHANGED = True
            LastContent = Content
    except:
        CrashReport("Canvas - Error in function Update.", str(traceback.format_exc()))