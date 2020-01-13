import os
import sys
from ij import IJ
from fiji.plugin.trackmate import Model
from fiji.plugin.trackmate import Settings
from fiji.plugin.trackmate import TrackMate
from fiji.plugin.trackmate import SelectionModel
from fiji.plugin.trackmate import Logger
from fiji.plugin.trackmate.detection import LogDetectorFactory
from fiji.plugin.trackmate.tracking.sparselap import SparseLAPTrackerFactory
from fiji.plugin.trackmate.tracking import LAPUtils
import fiji.plugin.trackmate.visualization.hyperstack.HyperStackDisplayer as HyperStackDisplayer
import fiji.plugin.trackmate.features.FeatureFilter as FeatureFilter
import fiji.plugin.trackmate.features.track.TrackDurationAnalyzer as TrackDurationAnalyzer
from  fiji.plugin.trackmate.action import LabelImgExporter

#@Float rad
#@Float thr 
#@Float dst
#@Float gapdst
#@Float gap
#@Float minlgth
#@String inDir
#@String outDir

rad = float(rad)			#15
thr = float(thr)			#0.1
dst = float(dst)			#25
gapdst = float(gapdst)		#35
gap = int(gap)				#2
minlgth = float(minlgth)	#3
#inDir = 'C:\Users\stosi\Desktop\in'
#outDir = 'C:\Users\stosi\Desktop\out'

for root, directories, filenames in os.walk(inDir):
	for filename in filenames:
		# Check for file extension
		if not filename.endswith('.tif'):
			continue
		imp = IJ.openImage(os.path.join(root, filename))
		IJ.run(imp, "Set Scale...", "distance=0 known=0 pixel=1 unit=pixel");
		IJ.run(imp, "Properties...", "channels=1 slices=1 frames="+str(imp.getNSlices())+" unit=pixel pixel_width=1.0000 pixel_height=1.0000 voxel_depth=1.0000");
		model = Model()
		settings = Settings()
		settings.setFrom(imp)
		settings.detectorFactory = LogDetectorFactory()
		settings.detectorSettings = { 
		    'DO_SUBPIXEL_LOCALIZATION' : True,
		    'RADIUS' : rad,
		    'TARGET_CHANNEL' : 1,
		    'THRESHOLD' : thr,
		    'DO_MEDIAN_FILTERING' : False,
		}
		#filter1 = FeatureFilter('QUALITY', 30, True)
		#settings.addSpotFilter(filter1)
		settings.trackerFactory = SparseLAPTrackerFactory()
		settings.trackerSettings = LAPUtils.getDefaultLAPSettingsMap() # almost good enough
		settings.trackerSettings['ALLOW_TRACK_SPLITTING'] = False
		settings.trackerSettings['ALLOW_TRACK_MERGING'] = False
		settings.trackerSettings['LINKING_MAX_DISTANCE'] = dst
		settings.trackerSettings['GAP_CLOSING_MAX_DISTANCE'] = gapdst
		settings.trackerSettings['MAX_FRAME_GAP']= gap
		settings.addTrackAnalyzer(TrackDurationAnalyzer())
		filter2 = FeatureFilter('DURATION_OF_TRACK', minlgth, True)
		settings.addTrackFilter(filter2)
		trackmate = TrackMate(model, settings)
		
		ok = trackmate.checkInput()
		if not ok:
		    sys.exit(str(trackmate.getErrorMessage()))
		    
		ok = trackmate.process()
		if not ok:
		    sys.exit(str(trackmate.getErrorMessage()))
		
		exportSpotsAsDots = True
		exportTracksOnly = True
		lblImg = LabelImgExporter.createLabelImagePlus( trackmate, exportSpotsAsDots, exportTracksOnly )
		IJ.saveAs(lblImg, "Tiff", os.path.join(outDir, filename));