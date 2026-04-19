import 'package:flutter/material.dart';
import 'screens/splash_screen.dart';

void main() {
  runApp(const WildFireApp());
}

class WildFireApp extends StatelessWidget {
  const WildFireApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'WildFire Predictor',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF080808),
        fontFamily: 'SF Pro Display',
      ),
      home: const SplashScreen(),
    );
  }
}