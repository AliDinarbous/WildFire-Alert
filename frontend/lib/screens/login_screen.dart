import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';
import '../widgets/flame_logo.dart';
import 'register_screen.dart';
import 'user_screen.dart';
import 'admin_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _loading = false;
  String? _error;
  bool _passwordError = false;

  Future<void> _login() async {
    setState(() { _loading = true; _error = null; _passwordError = false; });
    try {
      final res = await ApiService.login(
        _usernameController.text.trim(),
        _passwordController.text,
      );
      if (res['status'] == 200) {
        final token = res['body']['access_token'];
        await ApiService.saveToken(token);
        final prefs = await SharedPreferences.getInstance();
        // decode token to get user info via register endpoint not needed
        // we do a second call to get user info
        // For now navigate based on a re-login check
        // We'll store username and check admin via token claims
        // Simple approach: call /auth/login then parse
        // Since API returns only token, we store username manually
        await ApiService.saveUser(_usernameController.text.trim(), false);
        // Check if admin by trying admin endpoint
        final evalRes = await ApiService.evaluate();
        final isAdmin = evalRes['status'] != 403 && evalRes['status'] != 401;
        await ApiService.saveUser(_usernameController.text.trim(), isAdmin);
        if (!mounted) return;
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(
            builder: (_) => isAdmin ? const AdminScreen() : const UserScreen(),
          ),
        );
      } else {
        setState(() {
          _error = 'Identifiants incorrects';
          _passwordError = true;
          _loading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Erreur de connexion au serveur';
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
                _buildField(_usernameController, 'Username', false, false),
                const SizedBox(height: 12),
                _buildField(_passwordController, 'Password', true, _passwordError),
                const SizedBox(height: 20),
                SizedBox(
                  width: double.infinity,
                  height: 48,
                  child: ElevatedButton(
                    onPressed: _loading ? null : _login,
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
                            : const Text('Se connecter',
                                style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: Colors.white)),
                      ),
                    ),
                  ),
                ),
                if (_error != null) ...[
                  const SizedBox(height: 10),
                  Text(_error!, style: const TextStyle(fontSize: 12, color: Color(0xFFE8230A))),
                ],
                const Spacer(),
                GestureDetector(
                  onTap: () => Navigator.push(context,
                      MaterialPageRoute(builder: (_) => const RegisterScreen())),
                  child: RichText(
                    text: const TextSpan(
                      text: "Pas de compte ? ",
                      style: TextStyle(color: Color(0xFF666666), fontSize: 13),
                      children: [
                        TextSpan(text: "S'inscrire",
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