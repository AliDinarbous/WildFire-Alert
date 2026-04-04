class ApiConstants {
  static const String baseUrl = 'http://10.0.2.2:8000';

  static const String login = '/auth/login';
  static const String register = '/auth/register';
  static const String predict = '/predict/';
  static const String adminTrain = '/admin/train';
  static const String adminEval = '/admin/eval';
  static const String adminVersions = '/admin/models/versions';
  static const String adminReset = '/admin/models/reset';
}