import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';
import '../widgets/flame_logo.dart';
import 'login_screen.dart';

class AdminScreen extends StatefulWidget {
  const AdminScreen({super.key});

  @override
  State<AdminScreen> createState() => _AdminScreenState();
}

class _AdminScreenState extends State<AdminScreen> {
  String _username = 'admin';
  bool _trainLoading = false;
  bool _evalLoading = false;
  bool _versionsLoading = false;
  bool _resetLoading = false;
  String? _trainResult;
  String? _trainError;
  Map<String, dynamic>? _evalResult;
  String? _evalError;
  List<dynamic>? _versions;
  String? _versionsError;
  String? _resetMessage;
  bool _versionsExpanded = false;
  String? _selectedFileName;

  @override
  void initState() {
    super.initState();
    _loadUsername();
  }

  Future<void> _loadUsername() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() { _username = prefs.getString('username') ?? 'admin'; });
  }

  Future<void> _train() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['zip'],
    );
    if (result == null) return;
    final file = result.files.first;
    if (file.bytes == null) return;
    setState(() {
      _trainLoading = true;
      _trainResult = null;
      _trainError = null;
      _selectedFileName = file.name;
    });
    try {
      final res = await ApiService.trainModel(file.bytes!, file.name);
      if (res['status'] == 200) {
        final b = res['body'];
        setState(() {
          _trainResult = 'Modèle entraîné — ${b['version']} (${b['model_type']})';
          _trainLoading = false;
        });
      } else {
        setState(() { _trainError = 'Erreur entraînement'; _trainLoading = false; });
      }
    } catch (e) {
      setState(() { _trainError = 'Erreur serveur'; _trainLoading = false; });
    }
  }

  Future<void> _evaluate() async {
    setState(() { _evalLoading = true; _evalResult = null; _evalError = null; });
    try {
      final res = await ApiService.evaluate();
      if (res['status'] == 200) {
        setState(() { _evalResult = res['body']; _evalLoading = false; });
      } else {
        setState(() { _evalError = 'Erreur évaluation'; _evalLoading = false; });
      }
    } catch (e) {
      setState(() { _evalError = 'Erreur serveur'; _evalLoading = false; });
    }
  }

  Future<void> _loadVersions() async {
    setState(() {
      _versionsLoading = true;
      _versions = null;
      _versionsError = null;
      _versionsExpanded = true;
    });
    try {
      final res = await ApiService.getVersions();
      if (res['status'] == 200) {
        setState(() { _versions = res['body']; _versionsLoading = false; });
      } else {
        setState(() { _versionsError = 'Erreur chargement versions'; _versionsLoading = false; });
      }
    } catch (e) {
      setState(() { _versionsError = 'Erreur serveur'; _versionsLoading = false; });
    }
  }

  Future<void> _reset() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: const Color(0xFF161616),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Confirmer le reset',
            style: TextStyle(color: Colors.white, fontSize: 16)),
        content: const Text('Êtes-vous sûr de vouloir désactiver toutes les versions ?',
            style: TextStyle(color: Color(0xFF888888), fontSize: 13)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Annuler', style: TextStyle(color: Color(0xFF555555))),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Confirmer', style: TextStyle(color: Color(0xFFE8230A))),
          ),
        ],
      ),
    );
    if (confirm != true) return;
    setState(() { _resetLoading = true; _resetMessage = null; });
    try {
      final res = await ApiService.resetModel();
      if (res['status'] == 200) {
        setState(() { _resetMessage = 'Modèle réinitialisé avec succès'; _resetLoading = false; });
      } else {
        setState(() { _resetMessage = 'Erreur reset'; _resetLoading = false; });
      }
    } catch (e) {
      setState(() { _resetMessage = 'Erreur serveur'; _resetLoading = false; });
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
    final screenHeight = MediaQuery.of(context).size.height;

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
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: ConstrainedBox(
              constraints: BoxConstraints(minHeight: screenHeight),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 12),

                  // Header
                  Row(
                    children: [
                      const FlameLogo(size: 22),
                      const SizedBox(width: 8),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Bonjour, $_username',
                              style: const TextStyle(
                                  fontSize: 15, fontWeight: FontWeight.w700, color: Colors.white)),
                          const Text('Dashboard',
                              style: TextStyle(fontSize: 10, color: Color(0xFF555555))),
                        ],
                      ),
                      const Spacer(),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                        decoration: BoxDecoration(
                          color: const Color(0xFF2E1500),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Text('ADMIN',
                            style: TextStyle(
                                fontSize: 10, fontWeight: FontWeight.w600, color: Color(0xFFFF6B35))),
                      ),
                      const SizedBox(width: 10),
                      GestureDetector(
                        onTap: _logout,
                        child: const Icon(Icons.logout, color: Color(0xFF555555), size: 20),
                      ),
                    ],
                  ),
                  const SizedBox(height: 28),

                  // Card 1 — Entraîner
                  _buildCard(
                    icon: Icons.model_training,
                    title: 'Entraîner le modèle',
                    button: _orangeButton('Entraîner', _trainLoading, _train),
                    content: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const SizedBox(height: 16),
                        Container(
                          width: double.infinity,
                          height: 44,
                          decoration: BoxDecoration(
                            color: const Color(0xFF161616),
                            border: Border.all(color: const Color(0xFF333333), width: 0.5),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              const Icon(Icons.upload_file, color: Color(0xFF555555), size: 16),
                              const SizedBox(width: 8),
                              Text(
                                _selectedFileName ?? 'Sélectionner un fichier .zip',
                                style: const TextStyle(fontSize: 11, color: Color(0xFF555555)),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ],
                          ),
                        ),
                        if (_trainResult != null) ...[
                          const SizedBox(height: 10),
                          Text(_trainResult!,
                              style: const TextStyle(fontSize: 11, color: Color(0xFF4CAF50))),
                        ],
                        if (_trainError != null) ...[
                          const SizedBox(height: 10),
                          Text(_trainError!,
                              style: const TextStyle(fontSize: 11, color: Color(0xFFE8230A))),
                        ],
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),

                  // Card 2 — Évaluer
                  _buildCard(
                    icon: Icons.bar_chart,
                    title: 'Évaluation du modèle',
                    button: _orangeButton('Évaluer', _evalLoading, _evaluate),
                    content: _evalResult != null
                        ? Column(
                            children: [
                              const SizedBox(height: 16),
                              Row(
                                children: [
                                  _metricBox('Accuracy',
                                      '${((_evalResult!['accuracy'] ?? 0) * 100).toStringAsFixed(1)}%'),
                                  const SizedBox(width: 8),
                                  _metricBox('F1 Macro',
                                      '${((_evalResult!['f1_macro'] ?? _evalResult!['f1_score_macro'] ?? 0) * 100).toStringAsFixed(1)}%'),
                                  const SizedBox(width: 8),
                                  _metricBox('Precision',
                                      (_evalResult!['precision'] ?? _evalResult!['precision_macro'] ?? 0).toStringAsFixed(2)),
                                  const SizedBox(width: 8),
                                  _metricBox('Recall',
                                      (_evalResult!['recall'] ?? _evalResult!['recall_macro'] ?? 0).toStringAsFixed(2)),
                                ],
                              ),
                              if (_evalResult!['confusion_matrix'] != null) ...[
                                const SizedBox(height: 14),
                                const Align(
                                  alignment: Alignment.centerLeft,
                                  child: Text('Matrice de confusion',
                                      style: TextStyle(fontSize: 10, color: Color(0xFF555555))),
                                ),
                                const SizedBox(height: 8),
                                _confusionMatrix(_evalResult!['confusion_matrix']),
                              ],
                            ],
                          )
                        : _evalError != null
                            ? Padding(
                                padding: const EdgeInsets.only(top: 10),
                                child: Text(_evalError!,
                                    style: const TextStyle(
                                        fontSize: 11, color: Color(0xFFE8230A))),
                              )
                            : const SizedBox.shrink(),
                  ),
                  const SizedBox(height: 16),

                  // Card 3 — Versions
                  _buildCard(
                    icon: Icons.layers,
                    title: 'Versions des modèles',
                    button: _orangeButton('Afficher', _versionsLoading, _loadVersions),
                    content: _versionsExpanded
                        ? Column(
                            children: [
                              const SizedBox(height: 12),
                              if (_versionsLoading)
                                const Center(
                                  child: Padding(
                                    padding: EdgeInsets.all(8),
                                    child: CircularProgressIndicator(
                                        color: Color(0xFFFF6B35), strokeWidth: 2),
                                  ),
                                )
                              else if (_versionsError != null)
                                Text(_versionsError!,
                                    style: const TextStyle(
                                        fontSize: 11, color: Color(0xFFE8230A)))
                              else if (_versions != null && _versions!.isEmpty)
                                const Text('Aucune version disponible',
                                    style: TextStyle(fontSize: 11, color: Color(0xFF444444)))
                              else if (_versions != null)
                                ..._versions!.map((v) => _versionTile(v)).toList(),
                            ],
                          )
                        : const SizedBox.shrink(),
                  ),
                  const SizedBox(height: 16),

                  // Card 4 — Reset
                  _buildCard(
                    icon: Icons.restart_alt,
                    title: 'Reset du modèle',
                    button: _redButton('Reset', _resetLoading, _reset),
                    content: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const SizedBox(height: 10),
                        const Text(
                          'Désactive toutes les versions actives du modèle.',
                          style: TextStyle(fontSize: 11, color: Color(0xFF444444)),
                        ),
                        if (_resetMessage != null) ...[
                          const SizedBox(height: 10),
                          Text(_resetMessage!,
                              style: TextStyle(
                                  fontSize: 11,
                                  color: _resetMessage!.contains('succès')
                                      ? const Color(0xFF4CAF50)
                                      : const Color(0xFFE8230A))),
                        ],
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildCard({
    required IconData icon,
    required String title,
    required Widget button,
    required Widget content,
  }) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF111111),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF222222), width: 0.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Icon(icon, color: const Color(0xFFFF6B35), size: 18),
                  const SizedBox(width: 8),
                  Text(title,
                      style: const TextStyle(
                          fontSize: 13, fontWeight: FontWeight.w600, color: Colors.white)),
                ],
              ),
              button,
            ],
          ),
          content,
        ],
      ),
    );
  }

  Widget _orangeButton(String label, bool loading, VoidCallback onTap) {
    return GestureDetector(
      onTap: loading ? null : onTap,
      child: Container(
        height: 34,
        padding: const EdgeInsets.symmetric(horizontal: 14),
        decoration: BoxDecoration(
          gradient: const LinearGradient(colors: [Color(0xFFFF6B35), Color(0xFFE8230A)]),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Center(
          child: loading
              ? const SizedBox(
                  height: 14,
                  width: 14,
                  child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
              : Text(label,
                  style: const TextStyle(
                      fontSize: 12, fontWeight: FontWeight.w600, color: Colors.white)),
        ),
      ),
    );
  }

  Widget _redButton(String label, bool loading, VoidCallback onTap) {
    return GestureDetector(
      onTap: loading ? null : onTap,
      child: Container(
        height: 34,
        padding: const EdgeInsets.symmetric(horizontal: 14),
        decoration: BoxDecoration(
          color: const Color(0xFF1F0808),
          border: Border.all(color: const Color(0xFFE8230A), width: 0.5),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Center(
          child: loading
              ? const SizedBox(
                  height: 14,
                  width: 14,
                  child: CircularProgressIndicator(color: Color(0xFFE8230A), strokeWidth: 2))
              : Text(label,
                  style: const TextStyle(
                      fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFFE8230A))),
        ),
      ),
    );
  }

  Widget _metricBox(String label, String value) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 6),
        decoration: BoxDecoration(
          color: const Color(0xFF161616),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Column(
          children: [
            Text(value,
                style: const TextStyle(
                    fontSize: 14, fontWeight: FontWeight.w700, color: Color(0xFFFF6B35))),
            const SizedBox(height: 4),
            Text(label,
                style: const TextStyle(fontSize: 9, color: Color(0xFF555555))),
          ],
        ),
      ),
    );
  }

  Widget _confusionMatrix(List<dynamic> matrix) {
    final colors = [
      [const Color(0xFF0D2E0D), const Color(0xFF2E0D0D)],
      [const Color(0xFF2E0D0D), const Color(0xFF0D2E0D)]
    ];
    final textColors = [
      [const Color(0xFF4CAF50), const Color(0xFFE8230A)],
      [const Color(0xFFE8230A), const Color(0xFF4CAF50)]
    ];
    return Row(
      children: List.generate(
        2,
        (i) => Row(
          children: List.generate(
            2,
            (j) => Container(
              width: 52,
              height: 36,
              margin: const EdgeInsets.only(right: 4, bottom: 4),
              decoration: BoxDecoration(
                  color: colors[i][j], borderRadius: BorderRadius.circular(6)),
              child: Center(
                child: Text('${matrix[i][j]}',
                    style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                        color: textColors[i][j])),
              ),
            ),
          ).toList(),
        ),
      ).toList(),
    );
  }

  Widget _versionTile(Map<String, dynamic> v) {
    final isActive = v['is_active'] == true;
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFF161616),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('${v['version']} — ${v['model_type']}',
                  style: const TextStyle(
                      fontSize: 12, fontWeight: FontWeight.w600, color: Colors.white)),
              const SizedBox(height: 4),
              Text(v['created_at'].toString().substring(0, 10),
                  style: const TextStyle(fontSize: 10, color: Color(0xFF555555))),
            ],
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: isActive ? const Color(0xFF0D2E0D) : const Color(0xFF1F1F1F),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Text(
              isActive ? 'actif' : 'inactif',
              style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w600,
                  color: isActive ? const Color(0xFF4CAF50) : const Color(0xFF555555)),
            ),
          ),
        ],
      ),
    );
  }
}