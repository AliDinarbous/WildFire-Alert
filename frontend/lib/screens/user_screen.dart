import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../services/api_service.dart';
import '../widgets/flame_logo.dart';
import 'login_screen.dart';

class UserScreen extends StatefulWidget {
  const UserScreen({super.key});

  @override
  State<UserScreen> createState() => _UserScreenState();
}

class _UserScreenState extends State<UserScreen> {
  final _cityController = TextEditingController();
  final _mapController = MapController();
  bool _loading = false;
  String? _error;
  Map<String, dynamic>? _result;
  LatLng _center = const LatLng(46.2276, 2.2137);
  double _zoom = 5;

  Future<void> _predict() async {
    if (_cityController.text.trim().isEmpty) return;
    setState(() { _loading = true; _error = null; _result = null; });
    try {
      final res = await ApiService.predict(_cityController.text.trim());
      if (res['status'] == 200) {
        final body = res['body'];
        setState(() {
          _result = body;
          _center = LatLng(body['latitude'], body['longitude']);
          _zoom = 12;
          _loading = false;
        });
        _mapController.move(_center, _zoom);
      } else if (res['status'] == 404) {
        setState(() { _error = 'Ville introuvable'; _loading = false; });
      } else if (res['status'] == 503) {
        setState(() { _error = 'Service indisponible — modèle non chargé'; _loading = false; });
      } else {
        setState(() { _error = 'Erreur serveur'; _loading = false; });
      }
    } catch (e) {
      setState(() { _error = 'Erreur de connexion au serveur'; _loading = false; });
    }
  }

  Color _riskColor(String level) {
    switch (level) {
      case 'LOW': return const Color(0xFF4CAF50);
      case 'MEDIUM': return const Color(0xFFFF9800);
      case 'HIGH': return const Color(0xFFE8230A);
      case 'CRITICAL': return const Color(0xFF8B0000);
      default: return const Color(0xFF555555);
    }
  }

  Color _riskBg(String level) {
    switch (level) {
      case 'LOW': return const Color(0xFF0D2E0D);
      case 'MEDIUM': return const Color(0xFF2E1A00);
      case 'HIGH': return const Color(0xFF3D0F0F);
      case 'CRITICAL': return const Color(0xFF2A0000);
      default: return const Color(0xFF1F1F1F);
    }
  }

  Future<void> _logout() async {
    await ApiService.logout();
    if (!mounted) return;
    Navigator.pushReplacement(
        context, MaterialPageRoute(builder: (_) => const LoginScreen()));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF080808), Color(0xFF0D0D0D)],
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Column(
              children: [
                const SizedBox(height: 12),
                Row(
                  children: [
                    const FlameLogo(size: 22),
                    const SizedBox(width: 8),
                    const Text('WildFire',
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: Colors.white)),
                    const SizedBox(width: 4),
                    const Text('PREDICTOR',
                        style: TextStyle(fontSize: 9, color: Color(0xFFFF6B35), letterSpacing: 2)),
                    const Spacer(),
                    GestureDetector(
                      onTap: _logout,
                      child: const Icon(Icons.logout, color: Color(0xFF555555), size: 20),
                    ),
                  ],
                ),
                const SizedBox(height: 14),
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _cityController,
                        style: const TextStyle(color: Colors.white, fontSize: 13),
                        onSubmitted: (_) => _predict(),
                        decoration: InputDecoration(
                          hintText: 'Nom de la ville...',
                          hintStyle: const TextStyle(color: Color(0xFF555555), fontSize: 13),
                          prefixIcon: const Icon(Icons.search, color: Color(0xFF555555), size: 18),
                          filled: true,
                          fillColor: const Color(0xFF161616),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: const BorderSide(color: Color(0xFF2A2A2A)),
                          ),
                          enabledBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: const BorderSide(color: Color(0xFF2A2A2A)),
                          ),
                          focusedBorder: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: const BorderSide(color: Color(0xFFFF6B35)),
                          ),
                          contentPadding: const EdgeInsets.symmetric(vertical: 12),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    GestureDetector(
                      onTap: _loading ? null : _predict,
                      child: Container(
                        height: 46,
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [Color(0xFFFF6B35), Color(0xFFE8230A)],
                          ),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Center(
                          child: _loading
                              ? const SizedBox(height: 18, width: 18,
                                  child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                              : const Text('Analyser',
                                  style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Colors.white)),
                        ),
                      ),
                    ),
                  ],
                ),
                if (_error != null) ...[
                  const SizedBox(height: 6),
                  Align(
                    alignment: Alignment.centerLeft,
                    child: Text(_error!,
                        style: const TextStyle(fontSize: 11, color: Color(0xFFE8230A))),
                  ),
                ],
                const SizedBox(height: 10),
                Expanded(
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(16),
                    child: FlutterMap(
                      mapController: _mapController,
                      options: MapOptions(initialCenter: _center, initialZoom: _zoom),
                      children: [
                        TileLayer(
                          urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                          userAgentPackageName: 'com.example.frontend',
                        ),
                        if (_result != null)
                          MarkerLayer(
                            markers: [
                              Marker(
                                point: LatLng(_result!['latitude'], _result!['longitude']),
                                width: 40,
                                height: 40,
                                child: const Icon(Icons.location_pin,
                                    color: Color(0xFFE8230A), size: 40),
                              ),
                            ],
                          ),
                      ],
                    ),
                  ),
                ),
                if (_result != null) ...[
                  const SizedBox(height: 10),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: const Color(0xFF111111),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: const Color(0xFF2A2A2A), width: 0.5),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(_result!['city'],
                                style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: Colors.white)),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(
                                color: _riskBg(_result!['risk_level']),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Text(_result!['risk_level'],
                                  style: TextStyle(
                                      fontSize: 11,
                                      fontWeight: FontWeight.w600,
                                      color: _riskColor(_result!['risk_level']))),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.baseline,
                          textBaseline: TextBaseline.alphabetic,
                          children: [
                            Text('${(_result!['fire_probability'] * 100).toStringAsFixed(1)}',
                                style: const TextStyle(fontSize: 36, fontWeight: FontWeight.w700, color: Color(0xFFFF6B35))),
                            const Text('%',
                                style: TextStyle(fontSize: 18, color: Color(0xFFFF6B35))),
                            const SizedBox(width: 8),
                            const Text('probabilité de feu',
                                style: TextStyle(fontSize: 11, color: Color(0xFF555555))),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Row(
                          children: [
                            Text('${_result!['latitude'].toStringAsFixed(4)}° N',
                                style: const TextStyle(fontSize: 11, color: Color(0xFF444444))),
                            const SizedBox(width: 16),
                            Text('${_result!['longitude'].toStringAsFixed(4)}° E',
                                style: const TextStyle(fontSize: 11, color: Color(0xFF444444))),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
                const SizedBox(height: 12),
              ],
            ),
          ),
        ),
      ),
    );
  }
}