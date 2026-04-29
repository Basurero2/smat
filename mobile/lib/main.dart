import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() => runApp(const MaterialApp(home: SMATHome()));

class SMATHome extends StatefulWidget {
  const SMATHome({super.key});
  @override
  State<SMATHome> createState() => _SMATHomeState();
}

class _SMATHomeState extends State<SMATHome> {
  // USA TU IP REAL AQUÍ
  final String backendUrl = "http://192.168.0.114:8000/estaciones/";

  Future<List<dynamic>> fetchEstaciones() async {
    final response = await http.get(Uri.parse(backendUrl));
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Error al cargar estaciones');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('SMAT Móvil - UNMSM')),
      body: FutureBuilder(
        future: fetchEstaciones(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('❌ Error: ${snapshot.error}'));
          } else {
            final estaciones = snapshot.data as List;
            return ListView.builder(
              itemCount: estaciones.length,
              itemBuilder: (context, index) => ListTile(
                leading: const Icon(Icons.satellite_alt, color: Colors.blue),
                title: Text(estaciones[index]['nombre']),
                subtitle: Text(estaciones[index]['ubicacion']),
              ),
            );
          }
        },
      ),
      // --- ESTE ES EL RETO DEL LABORATORIO 5 ---
      floatingActionButton: FloatingActionButton(
        child: const Icon(Icons.refresh),
        onPressed: () {
          setState(() {}); // Esto fuerza a la App a pedir datos de nuevo
        },
      ),
    );
  }
}