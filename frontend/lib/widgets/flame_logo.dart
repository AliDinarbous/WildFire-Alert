import 'package:flutter/material.dart';

class FlameLogo extends StatelessWidget {
  final double size;
  const FlameLogo({super.key, this.size = 80});

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      size: Size(size, size * 1.25),
      painter: _FlamePainter(),
    );
  }
}

class _FlamePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;

    final outerPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [Color(0xFFFF6B35), Color(0xFFE8230A)],
      ).createShader(Rect.fromLTWH(0, 0, w, h));

    final outerPath = Path()
      ..moveTo(w * 0.5, 0)
      ..cubicTo(w * 0.5, 0, w * 0.875, h * 0.3, w * 0.875, h * 0.55)
      ..cubicTo(w * 0.875, h * 0.74, w * 0.7125, h * 0.9, w * 0.5, h * 0.9)
      ..cubicTo(w * 0.2875, h * 0.9, w * 0.125, h * 0.74, w * 0.125, h * 0.55)
      ..cubicTo(w * 0.125, h * 0.3, w * 0.5, 0, w * 0.5, 0)
      ..close();
    canvas.drawPath(outerPath, outerPaint);

    final midPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [Color(0xFFFFB347), Color(0xFFFF6B35)],
      ).createShader(Rect.fromLTWH(0, 0, w, h));

    final midPath = Path()
      ..moveTo(w * 0.5, h * 0.28)
      ..cubicTo(w * 0.5, h * 0.28, w * 0.725, h * 0.46, w * 0.725, h * 0.6)
      ..cubicTo(w * 0.725, h * 0.71, w * 0.625, h * 0.8, w * 0.5, h * 0.8)
      ..cubicTo(w * 0.375, h * 0.8, w * 0.275, h * 0.71, w * 0.275, h * 0.6)
      ..cubicTo(w * 0.275, h * 0.46, w * 0.5, h * 0.28, w * 0.5, h * 0.28)
      ..close();
    canvas.drawPath(midPath, midPaint);

    final tipPaint = Paint()..color = Color(0xFFFFF0C0);
    final tipPath = Path()
      ..moveTo(w * 0.5, h * 0.52)
      ..cubicTo(w * 0.5, h * 0.52, w * 0.625, h * 0.6, w * 0.625, h * 0.67)
      ..cubicTo(w * 0.625, h * 0.73, w * 0.569, h * 0.78, w * 0.5, h * 0.78)
      ..cubicTo(w * 0.431, h * 0.78, w * 0.375, h * 0.73, w * 0.375, h * 0.67)
      ..cubicTo(w * 0.375, h * 0.6, w * 0.5, h * 0.52, w * 0.5, h * 0.52)
      ..close();
    canvas.drawPath(tipPath, tipPaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}