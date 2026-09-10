from pathlib import Path

main = Path('TrainStopMeter_v1/app/src/main/java/com/dinnercoffee/trainstopmeter/MainActivity.java')
s = main.read_text()

# Invalidate any calibration made with the rear-camera geometry.
s = s.replace('    private static final String KEY_MANUAL_ZERO = "manual_zero_distance";\n',
              '    private static final String KEY_MANUAL_ZERO = "manual_zero_distance";\n'
              '    private static final String KEY_CAMERA_MODE = "camera_mode";\n'
              '    private static final String CAMERA_MODE_FRONT = "front_v1_2";\n')

old_prefs = '''        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);\n        manualZeroDistanceMeters = getDouble(KEY_MANUAL_ZERO, 0.0);\n        dayCalibration = CalibrationStore.load(prefs, KEY_DAY);\n        nightCalibration = CalibrationStore.load(prefs, KEY_NIGHT);\n'''
new_prefs = '''        prefs = getSharedPreferences(PREFS, MODE_PRIVATE);\n        // Rear- and front-camera perspective geometry cannot share calibration.\n        // On the first v1.2 launch, preserve PIN/manual distance but force a new zero registration.\n        if (!CAMERA_MODE_FRONT.equals(prefs.getString(KEY_CAMERA_MODE, \"\"))) {\n            prefs.edit()\n                    .remove(KEY_DAY)\n                    .remove(KEY_NIGHT)\n                    .putString(KEY_CAMERA_MODE, CAMERA_MODE_FRONT)\n                    .apply();\n        }\n        manualZeroDistanceMeters = getDouble(KEY_MANUAL_ZERO, 0.0);\n        dayCalibration = CalibrationStore.load(prefs, KEY_DAY);\n        nightCalibration = CalibrationStore.load(prefs, KEY_NIGHT);\n'''
if old_prefs not in s:
    raise SystemExit('prefs block not found')
s = s.replace(old_prefs, new_prefs)

old_bind = '''                Camera camera = provider.bindToLifecycle(this,\n                        CameraSelector.DEFAULT_BACK_CAMERA, preview, imageAnalysis);\n                focalPixelsPerImageWidth = CameraGeometry.focalPixelsPerImageWidth(camera);\n\n                updateAdminSummary(\"카메라 준비 완료\");\n'''
new_bind = '''                // The installed tablet faces the track with its display side, so use the front camera.\n                // PreviewView mirrors the selfie preview; undo that mirror so the live image lines up\n                // with ImageAnalysis / rail-overlay coordinates used for calibration and distance.\n                previewView.setScaleX(-1f);\n                Camera camera = provider.bindToLifecycle(this,\n                        CameraSelector.DEFAULT_FRONT_CAMERA, preview, imageAnalysis);\n                focalPixelsPerImageWidth = CameraGeometry.focalPixelsPerImageWidth(camera);\n\n                updateAdminSummary(\"v1.2 · 전면 카메라 준비 완료\");\n'''
if old_bind not in s:
    raise SystemExit('rear-camera bind block not found')
s = s.replace(old_bind, new_bind)

# Make the source/version unambiguous in the administrator screen.
s = s.replace('TrainStopMeter v1 field prototype.', 'TrainStopMeter v1.2 field prototype.')
main.write_text(s)

strings = Path('TrainStopMeter_v1/app/src/main/res/values/strings.xml')
t = strings.read_text()
t = t.replace('현장 검증용 프로토타입 · 기존 정차 안전설비를 대체하지 않음',
              'v1.2 · 전면 카메라 · 현장 검증용 프로토타입 · 기존 정차 안전설비를 대체하지 않음')
strings.write_text(t)

print('v1.2 front-camera patch applied')
