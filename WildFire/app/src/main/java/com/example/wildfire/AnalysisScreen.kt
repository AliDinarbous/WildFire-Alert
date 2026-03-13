package com.example.wildfire

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Cloud
import androidx.compose.material.icons.filled.Memory
import androidx.compose.material.icons.filled.SatelliteAlt
import androidx.compose.material.icons.filled.Whatshot
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.wildfire.ui.theme.WildFireOrange
import com.example.wildfire.ui.theme.WildFireTheme
import kotlinx.coroutines.delay

@Composable
fun AnalysisScreen(onAnalysisComplete: () -> Unit) {
    var progress by remember { mutableFloatStateOf(0f) }
    val animatedProgress by animateFloatAsState(
        targetValue = progress,
        animationSpec = tween(durationMillis = 5000),
        label = "ProgressAnimation"
    )

    LaunchedEffect(Unit) {
        progress = 1f
        delay(5500) // Slightly longer than animation to ensure it finishes
        onAnalysisComplete()
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.Whatshot,
            contentDescription = null,
            modifier = Modifier.size(80.dp),
            tint = WildFireOrange
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "Analyse en cours...",
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold,
            color = Color(0xFF2D3142)
        )

        Spacer(modifier = Modifier.height(48.dp))

        AnalysisStepItem(
            icon = Icons.Default.SatelliteAlt,
            text = "Récupération image satellite...",
            isActive = animatedProgress > 0.1f
        )
        Spacer(modifier = Modifier.height(16.dp))
        AnalysisStepItem(
            icon = Icons.Default.Cloud,
            text = "Récupération données météo...",
            isActive = animatedProgress > 0.4f
        )
        Spacer(modifier = Modifier.height(16.dp))
        AnalysisStepItem(
            icon = Icons.Default.Memory,
            text = "Analyse IA...",
            isActive = animatedProgress > 0.7f
        )

        Spacer(modifier = Modifier.height(64.dp))

        // Progress Text
        Text(
            text = "${(animatedProgress * 100).toInt()}%",
            fontSize = 18.sp,
            fontWeight = FontWeight.Bold,
            color = Color.Gray,
            modifier = Modifier
                .background(Color(0xFFF5F5F5), RoundedCornerShape(16.dp))
                .padding(horizontal = 16.dp, vertical = 4.dp)
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Progress Bar
        LinearProgressIndicator(
            progress = { animatedProgress },
            modifier = Modifier
                .fillMaxWidth()
                .height(12.dp),
            color = WildFireOrange,
            trackColor = Color(0xFFEEEEEE),
            strokeCap = androidx.compose.ui.graphics.StrokeCap.Round
        )
    }
}

@Composable
fun AnalysisStepItem(icon: ImageVector, text: String, isActive: Boolean) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = icon,
                contentDescription = null,
                tint = if (isActive) Color(0xFF43A047) else Color.Gray,
                modifier = Modifier.size(24.dp)
            )
            Spacer(modifier = Modifier.width(16.dp))
            Text(
                text = text,
                color = if (isActive) Color.Black else Color.Gray,
                fontWeight = if (isActive) FontWeight.Medium else FontWeight.Normal
            )
        }
    }
}

@Preview(showBackground = true)
@Composable
fun AnalysisScreenPreview() {
    WildFireTheme {
        AnalysisScreen(onAnalysisComplete = {})
    }
}
