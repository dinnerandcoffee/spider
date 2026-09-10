from pathlib import Path

main = Path('TrainStopMeter_v1/app/src/main/java/com/dinnercoffee/trainstopmeter/MainActivity.java')
s = main.read_text()

s = s.replace('import android.os.Bundle;\n', 'import android.os.Bundle;\nimport android.os.Handler;\nimport android.os.Looper;\n')
s = s.replace('import android.view.Surface;\n', 'import android.view.MotionEvent;\nimport android.view.Surface;\n')
s = s.replace('    private TextView adminStatus;\n', '    private TextView adminStatus;\n    private View adminHotspot;\n    private Button initialAdminButton;\n')
s = s.replace('    private boolean adminMode = false;\n', '    private boolean adminMode = false;\n    private final Handler adminHoldHandler = new Handler(Looper.getMainLooper());\n    private boolean adminHoldTriggered = false;\n')
s = s.replace('        adminStatus = findViewById(R.id.adminStatus);\n', '        adminStatus = findViewById(R.id.adminStatus);\n        adminHotspot = findViewById(R.id.adminHotspot);\n        initialAdminButton = findViewById(R.id.initialAdminButton);\n')

old = '''        View.OnLongClickListener adminLongPress = v -> {\n            showAdminLogin();\n            return true;\n        };\n        distanceText.setOnLongClickListener(adminLongPress);\n        normalPanel.setOnLongClickListener(adminLongPress);\n'''
new = '''        // Dedicated top-right invisible hotspot. Hold for a real 3 seconds.\n        adminHotspot.setOnTouchListener((v, event) -> {\n            switch (event.getActionMasked()) {\n                case MotionEvent.ACTION_DOWN:\n                    adminHoldTriggered = false;\n                    adminHoldHandler.postDelayed(() -> {\n                        adminHoldTriggered = true;\n                        v.performHapticFeedback(android.view.HapticFeedbackConstants.LONG_PRESS);\n                        showAdminLogin();\n                    }, 3000L);\n                    return true;\n                case MotionEvent.ACTION_UP:\n                    adminHoldHandler.removeCallbacksAndMessages(null);\n                    if (!adminHoldTriggered && dayCalibration == null && nightCalibration == null) {\n                        Toast.makeText(this, \"관리자: 우상단을 3초간 계속 누르세요.\", Toast.LENGTH_SHORT).show();\n                    }\n                    return true;\n                case MotionEvent.ACTION_CANCEL:\n                    adminHoldHandler.removeCallbacksAndMessages(null);\n                    return true;\n                default:\n                    return true;\n            }\n        });\n'''
if old not in s:
    raise SystemExit('admin long-press block not found')
s = s.replace(old, new)

s = s.replace('        dayButton.setOnClickListener(v -> registerZero(\"day\"));\n', '        initialAdminButton.setOnClickListener(v -> showAdminLogin());\n\n        dayButton.setOnClickListener(v -> registerZero(\"day\"));\n')
s = s.replace('        setAdminMode(false);\n\n        if (ContextCompat.checkSelfPermission', '        setAdminMode(false);\n        showWaiting();\n\n        if (ContextCompat.checkSelfPermission')
s = s.replace('                    Toast.makeText(this, \"정위치 등록 완료\", Toast.LENGTH_SHORT).show();\n', '                    if (initialAdminButton != null) initialAdminButton.setVisibility(View.GONE);\n                    Toast.makeText(this, \"정위치 등록 완료\", Toast.LENGTH_SHORT).show();\n')

old_wait = '''    private void showWaiting() {\n        distanceText.setText(R.string.waiting);\n        distanceText.setTextColor(Color.rgb(189, 189, 189));\n    }\n'''
new_wait = '''    private void showWaiting() {\n        if (dayCalibration == null && nightCalibration == null) {\n            distanceText.setText(\"초기설정 필요\");\n            distanceText.setTextSize(34f);\n            distanceText.setTextColor(Color.rgb(189, 189, 189));\n            if (initialAdminButton != null) initialAdminButton.setVisibility(View.VISIBLE);\n        } else {\n            distanceText.setTextSize(getResources().getDimension(R.dimen.distance_text_size)\n                    / getResources().getDisplayMetrics().scaledDensity);\n            distanceText.setText(R.string.waiting);\n            distanceText.setTextColor(Color.rgb(189, 189, 189));\n            if (initialAdminButton != null) initialAdminButton.setVisibility(View.GONE);\n        }\n    }\n'''
if old_wait not in s:
    raise SystemExit('showWaiting block not found')
s = s.replace(old_wait, new_wait)
s = s.replace('    private void showDistance(double d) {\n', '    private void showDistance(double d) {\n        if (initialAdminButton != null) initialAdminButton.setVisibility(View.GONE);\n        distanceText.setTextSize(getResources().getDimension(R.dimen.distance_text_size)\n                / getResources().getDisplayMetrics().scaledDensity);\n')

main.write_text(s)

layout = Path('TrainStopMeter_v1/app/src/main/res/layout/activity_main.xml')
x = layout.read_text()
needle = '''        <TextView\n            android:id=\"@+id/distanceText\"\n            android:layout_width=\"match_parent\"\n            android:layout_height=\"match_parent\"\n            android:gravity=\"center\"\n            android:fontFamily=\"sans-serif-condensed\"\n            android:includeFontPadding=\"false\"\n            android:text=\"@string/waiting\"\n            android:textColor=\"#BDBDBD\"\n            android:textSize=\"@dimen/distance_text_size\"\n            android:textStyle=\"bold\" />\n'''
add = needle + '''\n        <!-- Shown only before the first calibration. -->\n        <Button\n            android:id=\"@+id/initialAdminButton\"\n            android:layout_width=\"wrap_content\"\n            android:layout_height=\"52dp\"\n            android:layout_gravity=\"bottom|center_horizontal\"\n            android:layout_marginBottom=\"48dp\"\n            android:minWidth=\"160dp\"\n            android:text=\"관리자 설정\"\n            android:textSize=\"18sp\" />\n'''
if needle not in x:
    raise SystemExit('distanceText layout block not found')
x = x.replace(needle, add)

marker = '    <!-- Visible only after administrator PIN login. -->'
hotspot = '''    <!-- Invisible administrator entry area after calibration. -->\n    <View\n        android:id=\"@+id/adminHotspot\"\n        android:layout_width=\"112dp\"\n        android:layout_height=\"112dp\"\n        android:layout_gravity=\"top|end\"\n        android:background=\"@android:color/transparent\"\n        android:clickable=\"true\"\n        android:focusable=\"true\"\n        android:longClickable=\"true\" />\n\n'''
if marker not in x:
    raise SystemExit('admin panel marker not found')
x = x.replace(marker, hotspot + marker)
layout.write_text(x)

# Prototype v1.1 label
strings = Path('TrainStopMeter_v1/app/src/main/res/values/strings.xml')
t = strings.read_text()
t = t.replace('TrainStopMeter v1', 'TrainStopMeter v1.1')
strings.write_text(t)

print('v1.1 admin entry patch applied')
