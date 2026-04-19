import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../constants/api_constants.dart';

class ApiService {
  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('token');
  }

  static Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('token', token);
  }

  static Future<void> saveUser(String username, bool isAdmin) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('username', username);
    await prefs.setBool('isAdmin', isAdmin);
  }

  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }

  static Future<Map<String, dynamic>> login(
      String username, String password) async {
    final response = await http.post(
      Uri.parse('${ApiConstants.baseUrl}${ApiConstants.login}'),
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: {'username': username, 'password': password},
    );
    return {'status': response.statusCode, 'body': jsonDecode(response.body)};
  }

  static Future<Map<String, dynamic>> register(
      String username, String email, String password) async {
    final response = await http.post(
      Uri.parse('${ApiConstants.baseUrl}${ApiConstants.register}'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'username': username, 'email': email, 'password': password}),
    );
    return {'status': response.statusCode, 'body': jsonDecode(response.body)};
  }

  static Future<Map<String, dynamic>> predict(String city) async {
    final token = await getToken();
    final response = await http.post(
      Uri.parse('${ApiConstants.baseUrl}${ApiConstants.predict}'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({'city': city}),
    );
    return {'status': response.statusCode, 'body': jsonDecode(response.body)};
  }

  static Future<Map<String, dynamic>> evaluate() async {
    final token = await getToken();
    final response = await http.get(
      Uri.parse('${ApiConstants.baseUrl}${ApiConstants.adminEval}'),
      headers: {'Authorization': 'Bearer $token'},
    );
    return {'status': response.statusCode, 'body': jsonDecode(response.body)};
  }

  static Future<Map<String, dynamic>> getVersions() async {
    final token = await getToken();
    final response = await http.get(
      Uri.parse('${ApiConstants.baseUrl}${ApiConstants.adminVersions}'),
      headers: {'Authorization': 'Bearer $token'},
    );
    return {'status': response.statusCode, 'body': jsonDecode(response.body)};
  }

  static Future<Map<String, dynamic>> resetModel() async {
    final token = await getToken();
    final response = await http.put(
      Uri.parse('${ApiConstants.baseUrl}${ApiConstants.adminReset}'),
      headers: {'Authorization': 'Bearer $token'},
    );
    return {'status': response.statusCode, 'body': jsonDecode(response.body)};
  }

  static Future<Map<String, dynamic>> trainModel(
      List<int> fileBytes, String filename) async {
    final token = await getToken();
    final request = http.MultipartRequest(
      'POST',
      Uri.parse('${ApiConstants.baseUrl}${ApiConstants.adminTrain}'),
    );
    request.headers['Authorization'] = 'Bearer $token';
    request.files.add(http.MultipartFile.fromBytes(
      'file',
      fileBytes,
      filename: filename,
    ));
    final streamed = await request.send();
    final response = await http.Response.fromStream(streamed);
    return {'status': response.statusCode, 'body': jsonDecode(response.body)};
  }
}