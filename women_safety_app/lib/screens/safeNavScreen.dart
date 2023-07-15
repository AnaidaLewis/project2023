import 'package:flutter/material.dart';
import 'package:women_safety_app/components/app_bar.dart';
import 'package:women_safety_app/utils/color.dart';

class SafeNavScreen extends StatelessWidget {
  const SafeNavScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      appBar: AppBarConstant(),
      backgroundColor: rLightBlue,
      body: Center(child: Text("SafeNav page")),
    );
  }
}