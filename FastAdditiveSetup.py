#Author-Sualp Ozel
#Description-Create 2 Components in Design, Change workspace to MFG.

import adsk.core, adsk.fusion, traceback, math, adsk.cam

# scale of the bottle size
# scale = 2.0

# unit - cm
height = 10.5
topWidth = 1.4
topHight = 0.95
bodyTopWidth = 0.2
bottomWidth = 1.6
upperArcCenterToTop = 2.25
upperArcRadius = 8
lowerArcRadius = 7.5
filletRadius = 0.25
thickness = 0.15
#threadPitch = 0.2

# used for direct modeling
upperArcMidPtXOffset = -0.09
upperArcMidPtYOffset = -2.05
upperArcEndPtXOffset = 0.23
upperArcEndPtYOffset = -3.6
lowerArcMidPtXOffsetFromOriginPt = 2.33
lowerArcMidPtYOffsetFromOriginPt = 2.95

bottomCenter = adsk.core.Point3D.create(0, 0, 0)
bottleMaterial = 'PrismMaterial-006'
bottleAppearance = 'Prism-154'
materialLibId = 'C1EEA57C-3F56-45FC-B8CB-A9EC46A9994C'
appearanceLibId = 'BA5EE55E-9982-449B-9D66-9F036540E140'

nearZero = 0.000001

app = adsk.core.Application.get()
ui  = app.userInterface

newComp = None

def createNewComponent():
    # Get the active design.
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent
    allOccs = rootComp.occurrences
    newOcc = allOccs.addNewComponent(adsk.core.Matrix3D.create())
    return newOcc.component

def createBottle():
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    if not design:
        ui.messageBox('It is not supported in current workspace, please change to MODEL workspace and try again.')
        return
    currentDesignType = design.designType

    global newComp
    newComp = createNewComponent()
    if newComp is None:
        ui.messageBox('New component failed to create', 'New Component Failed')
        return

    # add sketch
    sketches = newComp.sketches
    sketch = sketches.add(newComp.xZConstructionPlane)

    # add sketch curves
    sketchlines = sketch.sketchCurves.sketchLines

    endPt = bottomCenter.copy() #start from bottomCenter
    endPt.y = bottomCenter.y + height
    heightLine = sketchlines.addByTwoPoints(bottomCenter, endPt)

    endPt.x = endPt.x + topWidth
    topLine = sketchlines.addByTwoPoints(heightLine.endSketchPoint, endPt)

    endPt.y = endPt.y - topHight
    topHightLine = sketchlines.addByTwoPoints(topLine.endSketchPoint, endPt)

    endPt.x = endPt.x + bodyTopWidth
    topBodyLine = sketchlines.addByTwoPoints(topHightLine.endSketchPoint, endPt)

    sketchArcs = sketch.sketchCurves.sketchArcs

    if currentDesignType == adsk.fusion.DesignTypes.DirectDesignType:
        endPt.x = topBodyLine.endSketchPoint.geometry.x + upperArcEndPtXOffset
        endPt.y = topBodyLine.endSketchPoint.geometry.y + upperArcEndPtYOffset
        ptOnArc = adsk.core.Point3D.create(topBodyLine.endSketchPoint.geometry.x + upperArcMidPtXOffset, topBodyLine.endSketchPoint.geometry.y + upperArcMidPtYOffset)
        upperArc = sketchArcs.addByThreePoints(topBodyLine.endSketchPoint, ptOnArc, endPt)

        endPt = bottomCenter.copy()
        endPt.x = bottomWidth
        ptOnArc = adsk.core.Point3D.create(lowerArcMidPtXOffsetFromOriginPt, lowerArcMidPtYOffsetFromOriginPt)
    else:
        deltPos = 0.1
        endPt.x = topWidth + bodyTopWidth + bodyTopWidth
        endPt.y = height / 2
        ptOnArc = adsk.core.Point3D.create(endPt.x - deltPos, endPt.y + deltPos)
        upperArc = sketchArcs.addByThreePoints(topBodyLine.endSketchPoint, ptOnArc, endPt)

        endPt = bottomCenter.copy()
        endPt.x = bottomWidth
        ptOnArc = adsk.core.Point3D.create(endPt.x + deltPos, endPt.y + deltPos)

    lowerArc = sketchArcs.addByThreePoints(upperArc.endSketchPoint, ptOnArc, endPt)
    buttomLine = sketchlines.addByTwoPoints(lowerArc.startSketchPoint, heightLine.startSketchPoint)

    # add constraints
    heightLine.startSketchPoint.isFixed = True
    sketchConstraints = sketch.geometricConstraints
    sketchConstraints.addHorizontal(buttomLine)
    sketchConstraints.addPerpendicular(buttomLine, heightLine)
    sketchConstraints.addPerpendicular(heightLine, topLine)
    sketchConstraints.addPerpendicular(topLine, topHightLine)
    sketchConstraints.addPerpendicular(topHightLine, topBodyLine)

    # add dimensions
    sketchDims = sketch.sketchDimensions

    startPt = heightLine.startSketchPoint.geometry
    endPt = heightLine.endSketchPoint.geometry
    textPos = adsk.core.Point3D.create((startPt.x + endPt.x) / 2, (startPt.y + endPt.y) / 2, 0)
    textPos.x = textPos.x - 1
    sketchDims.addDistanceDimension(heightLine.startSketchPoint, heightLine.endSketchPoint, adsk.fusion.DimensionOrientations.AlignedDimensionOrientation, textPos)

    startPt = topLine.startSketchPoint.geometry
    endPt = topLine.endSketchPoint.geometry
    textPos = adsk.core.Point3D.create((startPt.x + endPt.x) / 2, (startPt.y + endPt.y) / 2, 0)
    textPos.y = textPos.y + 1
    sketchDims.addDistanceDimension(topLine.startSketchPoint, topLine.endSketchPoint, adsk.fusion.DimensionOrientations.AlignedDimensionOrientation, textPos)

    startPt = topHightLine.startSketchPoint.geometry
    endPt = topHightLine.endSketchPoint.geometry
    textPos = adsk.core.Point3D.create((startPt.x + endPt.x) / 2, (startPt.y + endPt.y) / 2, 0)
    textPos.x = textPos.x + 1
    sketchDims.addDistanceDimension(topHightLine.startSketchPoint, topHightLine.endSketchPoint, adsk.fusion.DimensionOrientations.AlignedDimensionOrientation, textPos)

    startPt = topBodyLine.startSketchPoint.geometry
    endPt = topBodyLine.endSketchPoint.geometry
    textPos = adsk.core.Point3D.create((startPt.x + endPt.x) / 2, (startPt.y + endPt.y) / 2, 0)
    textPos.y = textPos.y + 1
    sketchDims.addDistanceDimension(topBodyLine.startSketchPoint, topBodyLine.endSketchPoint, adsk.fusion.DimensionOrientations.AlignedDimensionOrientation, textPos)

    startPt = buttomLine.startSketchPoint.geometry
    endPt = buttomLine.endSketchPoint.geometry
    textPos = adsk.core.Point3D.create((startPt.x + endPt.x) / 2, (startPt.y + endPt.y) / 2, 0)
    textPos.y = textPos.y - 1
    sketchDims.addDistanceDimension(buttomLine.startSketchPoint, buttomLine.endSketchPoint, adsk.fusion.DimensionOrientations.AlignedDimensionOrientation, textPos)

    startPt = topLine.endSketchPoint.geometry
    endPt = upperArc.centerSketchPoint.geometry
    textPos = adsk.core.Point3D.create((startPt.x + endPt.x) / 2, (startPt.y + endPt.y) / 2, 0)
    if currentDesignType == adsk.fusion.DesignTypes.DirectDesignType:
        sketchDims.addDistanceDimension(topLine.endSketchPoint, upperArc.centerSketchPoint, adsk.fusion.DimensionOrientations.VerticalDimensionOrientation, textPos)
    else:
        distDim = sketchDims.addDistanceDimension(topLine.endSketchPoint, upperArc.centerSketchPoint, adsk.fusion.DimensionOrientations.VerticalDimensionOrientation, textPos)
        distDim.parameter.value = upperArcCenterToTop

        startPt = upperArc.centerSketchPoint.geometry
        textPos = adsk.core.Point3D.create(startPt.x + deltPos, startPt.y, 0)
        radialArc = sketchDims.addRadialDimension(upperArc, textPos)
        radialArc.parameter.value = upperArcRadius

        startPt = lowerArc.centerSketchPoint.geometry
        textPos = adsk.core.Point3D.create(startPt.x + deltPos, startPt.y, 0)
        radialArc = sketchDims.addRadialDimension(lowerArc, textPos)
        radialArc.parameter.value = lowerArcRadius

    # create revolve
    revolveFeats = newComp.features.revolveFeatures

    revolveInput = revolveFeats.createInput(sketch.profiles[0], heightLine, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    revolveInput.setAngleExtent(True, adsk.core.ValueInput.createByReal(2 * math.pi))
    revolveFeat = revolveFeats.add(revolveInput)

  
def run(context):
    try:
        createBottle()
        createBottle()


        # next 3 - Change the workspace (next 2 lines are already above and are not needed here)
        workspaces = ui.workspaces
        camWorkspace = workspaces.itemById("CAMEnvironment")
        camWorkspace.activate()
        
        cmd_id1 = "CreateMfgWorkingModelFromDesignCmd"
        ui.commandDefinitions.itemById(cmd_id1).execute()

        cmd_id2 = "IronSetup"
        ui.commandDefinitions.itemById(cmd_id2).execute()
     
        cmd_id3 = "CommitCommand"
        ui.commandDefinitions.itemById(cmd_id3).execute()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

