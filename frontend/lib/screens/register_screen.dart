import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../widgets/flame_logo.dart';
import 'login_screen.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _loading = false;
  String? _usernameError;
  String? _emailError;
  String? _generalError;

  Future<void> _register() async {
    setState(() {
      _loading = true;
      _usernameError = null;
      _emailError = null;
      _generalError = null;
    });
    if (_usernameController.text.trim().isEmpty ||
        _emailController.text.trim().isEmpty ||
        _passwordController.text.isEmpty) {
      setState(() {
        _generalError = 'Tous les champs sont obligatoires';
        _loading = false;
      });
      return;
    }
    try {
      final res = await ApiService.register(
        _usernameController.text.trim(),
        _emailController.text.trim(),
        _passwordController.text,
      );
      if (res['status'] == 200) {
        if (!mounted) return;
        Navigator.pushReplacement(
            context, MaterialPageRoute(builder: (_) => const LoginScreen()));
      } else {
        final detail = res['body']['detail'] ?? '';
        setState(() {
          if (detail.toString().contains('Username')) {
            _usernameError = "Ce nom d'utilisateur est déjà utilisé";
          } else if (detail.toString().contains('Email')) {
            _emailError = 'Cet email est déjà associé à un compte';
          } else {
            _generalError = 'Erreur lors de l\'inscription';
          }
          _loading = false;
        });
      }
    } catch (e) {
      setState(() {
        _generalError = 'Erreur de connexion au serveur';
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [Color(0xFF080808), Color(0xFF080808), Color(0xFF1C0800), Color(0xFF2E0D00)],
            stops: [0.0, 0.5, 0.8, 1.0],
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 28),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Spacer(),
                const FlameLogo(size: 56),
                const SizedBox(height: 16),
                const Text('WildFire',
                    style: TextStyle(fontSize: 26, fontWeight: FontWeight.w700, color: Colors.white)),
                const SizedBox(height: 4),
                const Text('PREDICTOR',
                    style: TextStyle(fontSize: 11, color: Color(0xFFFF6B35), letterSpacing: 4)),
                const SizedBox(height: 40),
                _buildField(_usernameController, 'Username', false, _usernameError != null),
                if (_usernameError != null) ...[
                  const SizedBox(height: 4),
                  Align(alignment: Alignment.centerLeft,
                      child: Text(_usernameError!,
                          style: const TextStyle(fontSize: 11, color: Color(0xFFE8230A)))),
                ],
                const SizedBox(height: 12),
                _buildField(_emailController, 'Email', false, _emailError != null),
                if (_emailError != null) ...[
                  const SizedBox(height: 4),
                  Align(alignment: Alignment.centerLeft,
                      child: Text(_emailError!,
                          style: const TextStyle(fontSize: 11, color: Color(0xFFE8230A)))),
                ],
                const SizedBox(height: 12),
                _buildField(_passwordController, 'Password', true, false),
                const SizedBox(height: 20),
                SizedBox(
                  width: double.infinity,
                  height: 48,
                  child: ElevatedButton(
                    onPressed: _loading ? null : _register,
                    style: ElevatedButton.styleFrom(
                      padding: EdgeInsets.zero,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                      backgroundColor: Colors.transparent,
                      shadowColor: Colors.transparent,
                    ),
                    child: Ink(
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFFFF6B35), Color(0xFFE8230A)],
                        ),
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: Center(
                        child: _loading
                            ? const SizedBox(height: 20, width: 20,
                                child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                            : const Text("S'inscrire",
                                style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: Colors.white)),
                      ),
                    ),
                  ),
                ),
                if (_generalError != null) ...[
                  const SizedBox(height: 10),
                  Text(_generalError!, style: const TextStyle(fontSize: 12, color: Color(0xFFE8230A))),
                ],
                const Spacer(),
                GestureDetector(
                  onTap: () => Navigator.pushReplacement(context,
                      MaterialPageRoute(builder: (_) => const LoginScreen())),
                  child: RichText(
                    text: const TextSpan(
                      text: "Déjà un compte ? ",
                      style: TextStyle(color: Color(0xFF666666), fontSize: 13),
                      children: [
                        TextSpan(text: "Se connecter",
                            style: TextStyle(color: Color(0xFFFF6B35), fontWeight: FontWeight.w600)),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildField(TextEditingController controller, String hint,
      bool obscure, bool hasError) {
    return TextField(
      controller: controller,
      obscureText: obscure,
      style: const TextStyle(color: Colors.white, fontSize: 14),
      decoration: InputDecoration(
        hintText: hint,
        hintStyle: const TextStyle(color: Color(0xFF555555)),
        filled: true,
        fillColor: const Color(0xFF161616),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(
            color: hasError ? const Color(0xFFE8230A) : const Color(0xFF2A2A2A),
          ),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(
            color: hasError ? const Color(0xFFE8230A) : const Color(0xFF2A2A2A),
          ),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(
            color: hasError ? const Color(0xFFE8230A) : const Color(0xFFFF6B35),
          ),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      ),
    );
  }
}