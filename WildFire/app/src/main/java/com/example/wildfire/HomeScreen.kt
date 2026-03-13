package com.example.wildfire

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountCircle
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Remove
import androidx.compose.material.icons.filled.WbSunny
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.wildfire.ui.theme.WildFireOrange
import com.example.wildfire.ui.theme.WildFireTheme

@Composable
fun HomeScreen(onAnalyze: () -> Unit) {
    var radiusKm by remember { mutableFloatStateOf(50f) }

    Box(modifier = Modifier.fillMaxSize()) {
        // Map Placeholder (In a real app, use Google Maps SDK)
        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(Color(0xFFE0F2F1)) // Simulating map background
        ) {
            // Circle overlay
            Canvas(modifier = Modifier.fillMaxSize()) {
                val center = Offset(size.width / 2, size.height * 0.4f)
                // Convert km to pixels (approximate for demo)
                val radiusPx = radiusKm * 5f

                // Draw filled circle (semi-transparent)
                drawCircle(
                    color = WildFireOrange.copy(alpha = 0.2f),
                    radius = radiusPx,
                    center = center
                )
                // Draw circle border
                drawCircle(
                    color = WildFireOrange,
                    radius = radiusPx,
                    center = center,
                    style = Stroke(width = 4f)
                )
            }

            // Location Marker in the center of the circle
            Icon(
                imageVector = Icons.Default.LocationOn,
                contentDescription = null,
                tint = Color(0xFF4285F4),
                modifier = Modifier
                    .size(40.dp)
                    .align(Alignment.TopCenter)
                    .offset(y = 230.dp)
            )
        }

        // Top UI Elements (User Profile)
        IconButton(
            onClick = { /* Profile */ },
            modifier = Modifier
                .align(Alignment.TopEnd)
                .padding(top = 48.dp, end = 16.dp)
                .size(48.dp)
                .background(Color.White, CircleShape)
        ) {
            Icon(Icons.Default.AccountCircle, contentDescription = "Profile", tint = Color.Gray)
        }

        // Zoom Controls
        Column(
            modifier = Modifier
                .align(Alignment.CenterEnd)
                .padding(end = 16.dp)
                .background(Color.White, RoundedCornerShape(8.dp))
                .width(40.dp)
        ) {
            IconButton(onClick = { }) { Icon(Icons.Default.Add, contentDescription = "Zoom In") }
            HorizontalDivider(modifier = Modifier.padding(horizontal = 8.dp))
            IconButton(onClick = { }) { Icon(Icons.Default.Remove, contentDescription = "Zoom Out") }
        }

        // Bottom Sheet Info
        Card(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .fillMaxWidth()
                .clip(RoundedCornerShape(topStart = 24.dp, topEnd = 24.dp)),
            colors = CardDefaults.cardColors(containerColor = Color.White),
            elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
        ) {
            Column(
                modifier = Modifier
                    .padding(24.dp)
                    .fillMaxWidth()
            ) {
                // Drag handle
                Box(
                    modifier = Modifier
                        .width(40.dp)
                        .height(4.dp)
                        .background(Color.LightGray, RoundedCornerShape(2.dp))
                        .align(Alignment.CenterHorizontally)
                )

                Spacer(modifier = Modifier.height(16.dp))

                // City and Location Icon
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        Icons.Default.LocationOn,
                        contentDescription = null,
                        tint = WildFireOrange,
                        modifier = Modifier.size(24.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "Bordeaux, France",
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF2D3142)
                    )
                }

                Spacer(modifier = Modifier.height(8.dp))

                // Weather Tag
                Surface(
                    color = Color(0xFFFFF3E0),
                    shape = RoundedCornerShape(8.dp)
                ) {
                    Row(
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                        verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            Icons.Default.WbSunny,
                            contentDescription = null,
                            tint = Color(0xFFFFB300),
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            text = "36°C | Ensoleillé",
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Medium,
                            color = Color(0xFF8D6E63)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(24.dp))

                // Radius Selector
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = "Rayon de surveillance:",
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF2D3142)
                    )
                    Text(
                        text = "${radiusKm.toInt()} km",
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF2D3142)
                    )
                }

                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("1km", fontSize = 12.sp, color = Color.Gray)
                    Slider(
                        value = radiusKm,
                        onValueChange = { radiusKm = it },
                        valueRange = 1f..100f,
                        modifier = Modifier.weight(1f),
                        colors = SliderDefaults.colors(
                            thumbColor = WildFireOrange,
                            activeTrackColor = WildFireOrange,
                            inactiveTrackColor = Color.LightGray
                        )
                    )
                    Text("100km", fontSize = 12.sp, color = Color.Gray)
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Analyze Button
                Button(
                    onClick = { onAnalyze() },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp),
                    shape = RoundedCornerShape(16.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = WildFireOrange)
                ) {
                    Text(
                        text = "Analyser le risque",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = Color.White
                    )
                }
            }
        }
    }
}

@Preview(showBackground = true)
@Composable
fun HomeScreenPreview() {
    WildFireTheme {
        HomeScreen(onAnalyze = {})
    }
}
