package com.example.wildfire

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import com.example.wildfire.ui.theme.WildFireTheme

enum class Screen {
    Login, Home, Analysis, Result
}

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            WildFireTheme {
                var currentScreen by remember { mutableStateOf(Screen.Login) }

                Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
                    when (currentScreen) {
                        Screen.Login -> LoginScreen(onLoginSuccess = { currentScreen = Screen.Home })
                        Screen.Home -> HomeScreen(onAnalyze = { currentScreen = Screen.Analysis })
                        Screen.Analysis -> AnalysisScreen(onAnalysisComplete = { currentScreen = Screen.Result })
                        Screen.Result -> ResultScreen(onBack = { currentScreen = Screen.Home })
                    }
                }
            }
        }
    }
}
