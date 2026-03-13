package com.example.wildfire

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material.icons.filled.Whatshot
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.wildfire.ui.theme.WildFireOrange
import com.example.wildfire.ui.theme.WildFireTheme

@Composable
fun ResultScreen(onBack: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
    ) {
        // Header with Gradient
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(200.dp)
                .background(
                    brush = Brush.verticalGradient(
                        colors = listOf(WildFireOrange, Color(0xFFFF7043))
                    )
                ),
            contentAlignment = Alignment.Center
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Icon(
                    imageVector = Icons.Default.Whatshot,
                    contentDescription = null,
                    tint = Color.White,
                    modifier = Modifier.size(64.dp)
                )
                Text(
                    text = "RISQUE ÉLEVÉ",
                    color = Color.White,
                    fontSize = 28.sp,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "8,7/10",
                    color = Color.White,
                    fontSize = 20.sp
                )
            }
        }

        Column(modifier = Modifier.padding(20.dp)) {
            // Context Card
            Card(
                colors = CardDefaults.cardColors(containerColor = Color(0xFFFFF3E0)),
                shape = RoundedCornerShape(12.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = "Cette situation rappelle l'incendie dévastateur de Gironde en juillet 2022 qui a brûlé 14 000 hectares dans des conditions similaires.",
                    modifier = Modifier.padding(16.dp),
                    fontSize = 14.sp,
                    color = Color(0xFF5D4037)
                )
            }

            Spacer(modifier = Modifier.height(24.dp))

            SectionTitle("POURQUOI C'EST CRITIQUE")
            ResultItem(text = "Végétation EXTRÊMEMENT sèche (18 jours sans pluie)")
            ResultItem(text = "Forêt de pins très inflammable")
            ResultItem(text = "Vents violents (45 km/h) = propagation ultra-rapide")

            Spacer(modifier = Modifier.height(24.dp))

            SectionTitle("DANGERS IMMÉDIATS")
            Card(
                colors = CardDefaults.cardColors(containerColor = Color(0xFFF5F5F5)),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.Warning, contentDescription = null, tint = WildFireOrange)
                    Spacer(modifier = Modifier.width(12.dp))
                    Text("Propagation possible", color = WildFireOrange, fontWeight = FontWeight.Bold)
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            SectionTitle("ACTIONS URGENTES")
            ActionItem("INTERDICTION : barbecues, cigarettes")
            ActionItem("Surveillez : fumée = appel 18 immédiatement")
            ActionItem("Préparez sac d'évacuation")

            Spacer(modifier = Modifier.height(32.dp))

            // Back Button
            OutlinedButton(
                onClick = onBack,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                shape = RoundedCornerShape(12.dp)
            ) {
                Icon(Icons.Default.ArrowBack, contentDescription = null)
                Spacer(modifier = Modifier.width(8.dp))
                Text("Retour", fontSize = 18.sp)
            }
            
            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}

@Composable
fun SectionTitle(title: String) {
    Text(
        text = title,
        fontSize = 14.sp,
        fontWeight = FontWeight.Bold,
        color = Color.Gray,
        modifier = Modifier.padding(bottom = 12.dp)
    )
}

@Composable
fun ResultItem(text: String) {
    Row(modifier = Modifier.padding(vertical = 4.dp), verticalAlignment = Alignment.CenterVertically) {
        Box(
            modifier = Modifier
                .size(8.dp)
                .background(WildFireOrange, RoundedCornerShape(4.dp))
        )
        Spacer(modifier = Modifier.width(12.dp))
        Text(text = text, fontSize = 15.sp)
    }
}

@Composable
fun ActionItem(text: String) {
    Card(
        modifier = Modifier.padding(vertical = 4.dp).fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Row(modifier = Modifier.padding(12.dp), verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.Check, contentDescription = null, tint = Color(0xFF43A047), modifier = Modifier.size(20.dp))
            Spacer(modifier = Modifier.width(12.dp))
            Text(text = text, fontSize = 14.sp)
        }
    }
}

@Preview(showBackground = true)
@Composable
fun ResultScreenPreview() {
    WildFireTheme {
        ResultScreen(onBack = {})
    }
}
