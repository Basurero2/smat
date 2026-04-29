import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/main.dart';
import 'package:flutter/material.dart';

void main() {
  testWidgets('SMAT Mobile Load Test', (WidgetTester tester) async {
    // Cambiamos MyApp por MaterialApp con SMATHome que es tu clase real
    await tester.pumpWidget(const MaterialApp(home: SMATHome()));

    // Verifica que al menos aparezca el título de la App
    expect(find.text('SMAT Móvil - UNMSM'), findsOneWidget);
  });
}
