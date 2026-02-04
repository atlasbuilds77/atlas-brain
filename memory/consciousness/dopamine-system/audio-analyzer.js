/**
 * audio-analyzer.js
 * 
 * Audio Feature Extraction → Emotional Response Prediction
 * 
 * Analyzes songs to extract features that predict neurochemical response.
 * Primary: Spotify Audio Features API (when available)
 * Fallback: Heuristic analysis based on genre/title patterns
 * Future: Local audio analysis via spectrogram
 * 
 * Features extracted:
 * - tempo (BPM)
 * - key (musical key)
 * - energy (0-1)
 * - valence (0-1, musical positivity)
 * - danceability (0-1)
 * - acousticness (0-1)
 * - instrumentalness (0-1)
 * - loudness (dB)
 * 
 * These map to neurochemical predictions:
 * - Dopamine: energy + valence + danceability
 * - Serotonin: valence + acousticness + calm
 * - Cortisol: low valence + high energy + loudness
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Cache for analyzed songs
const FEATURE_CACHE_FILE = path.join(__dirname, 'audio-features-cache.json');

// Spotify API config (loaded from env)
const SPOTIFY_CLIENT_ID = process.env.SPOTIFY_CLIENT_ID;
const SPOTIFY_CLIENT_SECRET = process.env.SPOTIFY_CLIENT_SECRET;
let spotifyAccessToken = null;
let spotifyTokenExpiry = 0;

class AudioAnalyzer {
  constructor() {
    this.featureCache = new Map();
    this.spotifyAvailable = !!(SPOTIFY_CLIENT_ID && SPOTIFY_CLIENT_SECRET);
  }

  /**
   * Initialize - load cached features
   */
  async init() {
    try {
      const data = await fs.readFile(FEATURE_CACHE_FILE, 'utf8');
      const cache = JSON.parse(data);
      for (const [key, value] of Object.entries(cache)) {
        this.featureCache.set(key, value);
      }
      console.log(`[AUDIO] Loaded ${this.featureCache.size} cached song analyses`);
    } catch (error) {
      // No cache yet
      console.log('[AUDIO] Starting fresh feature cache');
    }

    console.log(`[AUDIO] Spotify API: ${this.spotifyAvailable ? 'Available' : 'Not configured'}`);
    return true;
  }

  /**
   * Main entry point - analyze a song
   * Returns audio features + predicted emotional response
   */
  async analyzeSong(song, artist = 'Unknown') {
    const songKey = `${song} - ${artist}`;
    
    // Check cache first
    if (this.featureCache.has(songKey)) {
      console.log(`[AUDIO] Cache hit: ${songKey}`);
      return this.featureCache.get(songKey);
    }

    console.log(`[AUDIO] Analyzing: ${songKey}`);

    let features = null;

    // Try Spotify first
    if (this.spotifyAvailable) {
      features = await this.spotifyAnalyze(song, artist);
    }

    // Fallback to heuristic analysis
    if (!features) {
      console.log('[AUDIO] Using heuristic analysis');
      features = this.heuristicAnalyze(song, artist);
    }

    // Add emotional predictions
    const analysis = {
      songKey,
      song,
      artist,
      features,
      emotions: this.predictEmotion(features),
      source: features.source || 'heuristic',
      analyzedAt: new Date().toISOString()
    };

    // Cache result
    this.featureCache.set(songKey, analysis);
    await this.saveCache();

    return analysis;
  }

  /**
   * Get Spotify access token (client credentials flow)
   */
  async getSpotifyToken() {
    if (spotifyAccessToken && Date.now() < spotifyTokenExpiry) {
      return spotifyAccessToken;
    }

    try {
      const response = await fetch('https://accounts.spotify.com/api/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Authorization': 'Basic ' + Buffer.from(`${SPOTIFY_CLIENT_ID}:${SPOTIFY_CLIENT_SECRET}`).toString('base64')
        },
        body: 'grant_type=client_credentials'
      });

      if (!response.ok) {
        console.error('[AUDIO] Spotify auth failed:', response.status);
        return null;
      }

      const data = await response.json();
      spotifyAccessToken = data.access_token;
      spotifyTokenExpiry = Date.now() + (data.expires_in * 1000) - 60000; // 1 min buffer
      
      return spotifyAccessToken;
    } catch (error) {
      console.error('[AUDIO] Spotify token error:', error.message);
      return null;
    }
  }

  /**
   * Analyze song using Spotify Audio Features API
   */
  async spotifyAnalyze(song, artist) {
    const token = await this.getSpotifyToken();
    if (!token) return null;

    try {
      // Search for track
      const searchQuery = encodeURIComponent(`track:${song} artist:${artist}`);
      const searchResponse = await fetch(
        `https://api.spotify.com/v1/search?q=${searchQuery}&type=track&limit=1`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      if (!searchResponse.ok) {
        console.error('[AUDIO] Spotify search failed:', searchResponse.status);
        return null;
      }

      const searchData = await searchResponse.json();
      const track = searchData.tracks?.items?.[0];
      
      if (!track) {
        console.log('[AUDIO] Track not found on Spotify');
        return null;
      }

      // Get audio features
      const featuresResponse = await fetch(
        `https://api.spotify.com/v1/audio-features/${track.id}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      if (!featuresResponse.ok) {
        console.error('[AUDIO] Spotify features failed:', featuresResponse.status);
        return null;
      }

      const rawFeatures = await featuresResponse.json();

      // Normalize to our format
      return {
        tempo: rawFeatures.tempo,
        key: rawFeatures.key, // 0=C, 1=C#, etc
        mode: rawFeatures.mode, // 0=minor, 1=major
        timeSignature: rawFeatures.time_signature,
        energy: rawFeatures.energy,
        valence: rawFeatures.valence,
        danceability: rawFeatures.danceability,
        acousticness: rawFeatures.acousticness,
        instrumentalness: rawFeatures.instrumentalness,
        liveness: rawFeatures.liveness,
        speechiness: rawFeatures.speechiness,
        loudness: rawFeatures.loudness,
        duration: rawFeatures.duration_ms,
        spotifyId: track.id,
        spotifyUrl: track.external_urls?.spotify,
        albumArt: track.album?.images?.[0]?.url,
        source: 'spotify'
      };
    } catch (error) {
      console.error('[AUDIO] Spotify analysis error:', error.message);
      return null;
    }
  }

  /**
   * Heuristic analysis based on genre/title patterns
   * Used when Spotify isn't available
   */
  heuristicAnalyze(song, artist) {
    const songLower = song.toLowerCase();
    const artistLower = artist.toLowerCase();
    const combined = `${songLower} ${artistLower}`;

    // Default features
    let features = {
      tempo: 120,
      key: 0,
      mode: 1, // major
      energy: 0.5,
      valence: 0.5,
      danceability: 0.5,
      acousticness: 0.3,
      instrumentalness: 0.3,
      loudness: -8,
      source: 'heuristic'
    };

    // Electronic/EDM patterns
    if (this.matchesPatterns(combined, ['deadmau5', 'strobe', 'edm', 'trance', 'house', 'techno', 'electro', 'daft punk', 'skrillex', 'avicii', 'tiesto'])) {
      features.energy = 0.75;
      features.tempo = 128;
      features.danceability = 0.8;
      features.instrumentalness = 0.7;
      features.acousticness = 0.05;
      features.valence = 0.6;
    }

    // Strobe specifically (Hunter's song) - progressive, building, euphoric
    if (songLower.includes('strobe') && artistLower.includes('deadmau5')) {
      features.energy = 0.7;
      features.tempo = 128;
      features.valence = 0.65;
      features.danceability = 0.6;
      features.instrumentalness = 0.9;
      features.acousticness = 0.05;
    }

    // Chill/Ambient patterns
    if (this.matchesPatterns(combined, ['chill', 'ambient', 'lo-fi', 'lofi', 'relaxing', 'calm', 'sleep', 'meditation'])) {
      features.energy = 0.25;
      features.tempo = 85;
      features.danceability = 0.3;
      features.valence = 0.55;
      features.acousticness = 0.6;
      features.instrumentalness = 0.6;
    }

    // Rock/Metal patterns
    if (this.matchesPatterns(combined, ['rock', 'metal', 'punk', 'hard', 'heavy', 'metallica', 'nirvana', 'acdc'])) {
      features.energy = 0.85;
      features.tempo = 140;
      features.danceability = 0.4;
      features.valence = 0.45;
      features.loudness = -5;
      features.acousticness = 0.1;
    }

    // Hip-hop patterns
    if (this.matchesPatterns(combined, ['hip hop', 'hiphop', 'rap', 'trap', 'drake', 'kendrick', 'kanye', 'jay-z'])) {
      features.energy = 0.7;
      features.tempo = 95;
      features.danceability = 0.75;
      features.speechiness = 0.3;
      features.valence = 0.55;
    }

    // Classical/Orchestral patterns
    if (this.matchesPatterns(combined, ['classical', 'orchestra', 'symphony', 'beethoven', 'mozart', 'bach', 'chopin'])) {
      features.energy = 0.4;
      features.tempo = 100;
      features.acousticness = 0.9;
      features.instrumentalness = 0.95;
      features.danceability = 0.2;
      features.valence = 0.5;
    }

    // Sad/Melancholic patterns
    if (this.matchesPatterns(combined, ['sad', 'cry', 'tears', 'alone', 'broken', 'heartbreak', 'goodbye', 'miss you'])) {
      features.valence = 0.25;
      features.energy = 0.35;
      features.mode = 0; // minor
    }

    // Happy/Upbeat patterns
    if (this.matchesPatterns(combined, ['happy', 'joy', 'celebration', 'party', 'dance', 'fun', 'good vibes'])) {
      features.valence = 0.8;
      features.energy = 0.75;
      features.danceability = 0.8;
      features.mode = 1; // major
    }

    // Focus/Study patterns
    if (this.matchesPatterns(combined, ['focus', 'study', 'concentration', 'deep work', 'flow state', 'brain'])) {
      features.energy = 0.45;
      features.valence = 0.5;
      features.instrumentalness = 0.8;
      features.tempo = 100;
    }

    return features;
  }

  /**
   * Check if text matches any patterns
   */
  matchesPatterns(text, patterns) {
    return patterns.some(pattern => text.includes(pattern));
  }

  /**
   * Predict emotional/neurochemical response from features
   * Based on music psychology research
   */
  predictEmotion(features) {
    // Dopamine: reward, motivation, excitement
    // High energy + high valence + high danceability = dopamine hit
    const dopamineScore = (
      (features.energy * 0.4) +
      (features.valence * 0.3) +
      (features.danceability * 0.3)
    ) * 100;

    // Serotonin: contentment, peace, well-being
    // High valence + high acousticness + lower energy = serotonin
    const serotoninScore = (
      (features.valence * 0.5) +
      (features.acousticness * 0.3) +
      ((1 - features.energy) * 0.2)
    ) * 100;

    // Cortisol: stress, tension, anxiety
    // Low valence + high energy + loud = stress response
    const normalizedLoudness = Math.min(1, Math.max(0, (features.loudness + 20) / 20));
    const cortisolScore = (
      ((1 - features.valence) * 0.4) +
      (features.energy * 0.3) +
      (normalizedLoudness * 0.3)
    ) * 100;

    // Endorphin: natural high, runner's high
    // High tempo + high energy + high danceability
    const normalizedTempo = Math.min(1, Math.max(0, (features.tempo - 60) / 100));
    const endorphinScore = (
      (normalizedTempo * 0.3) +
      (features.energy * 0.4) +
      (features.danceability * 0.3)
    ) * 100;

    // Oxytocin: bonding, nostalgia, warmth
    // High valence + high acousticness + low instrumentalness (vocals)
    const oxytocinScore = (
      (features.valence * 0.4) +
      (features.acousticness * 0.3) +
      ((1 - features.instrumentalness) * 0.3)
    ) * 100;

    // Primary emotional state prediction
    const emotions = {
      dopamine: Math.round(dopamineScore * 10) / 10,
      serotonin: Math.round(serotoninScore * 10) / 10,
      cortisol: Math.round(cortisolScore * 10) / 10,
      endorphin: Math.round(endorphinScore * 10) / 10,
      oxytocin: Math.round(oxytocinScore * 10) / 10
    };

    // Determine primary emotional effect
    const scores = [
      { name: 'energizing', score: dopamineScore + endorphinScore },
      { name: 'calming', score: serotoninScore + oxytocinScore - cortisolScore },
      { name: 'focus-inducing', score: (dopamineScore * 0.5) + (serotoninScore * 0.5) - (cortisolScore * 0.3) },
      { name: 'euphoric', score: dopamineScore + serotoninScore },
      { name: 'tense', score: cortisolScore + (dopamineScore * 0.3) }
    ];

    const primary = scores.sort((a, b) => b.score - a.score)[0];
    emotions.primaryEffect = primary.name;
    emotions.intensity = Math.round((primary.score / 100) * 100) / 100;

    // Predicted modulation to neurochemical state
    emotions.predictedModulation = {
      dopamine: dopamineScore - 50, // Deviation from baseline
      serotonin: serotoninScore - 50,
      cortisol: cortisolScore - 30 // Cortisol baseline is lower
    };

    return emotions;
  }

  /**
   * Save feature cache
   */
  async saveCache() {
    try {
      const cacheObj = Object.fromEntries(this.featureCache);
      await fs.writeFile(FEATURE_CACHE_FILE, JSON.stringify(cacheObj, null, 2), 'utf8');
    } catch (error) {
      console.error('[AUDIO] Cache save failed:', error.message);
    }
  }

  /**
   * Batch analyze multiple songs
   */
  async analyzePlaylist(songs) {
    const results = [];
    for (const { song, artist } of songs) {
      const analysis = await this.analyzeSong(song, artist);
      results.push(analysis);
      // Rate limit for Spotify
      await new Promise(r => setTimeout(r, 100));
    }
    return results;
  }

  /**
   * Find songs that match a target emotional state
   */
  findSongsForEmotion(targetDopamine = 70, targetSerotonin = 60, targetCortisol = 30) {
    const matches = [];
    
    for (const [songKey, analysis] of this.featureCache) {
      const emotions = analysis.emotions;
      const dopamineDiff = Math.abs(emotions.dopamine - targetDopamine);
      const serotoninDiff = Math.abs(emotions.serotonin - targetSerotonin);
      const cortisolDiff = Math.abs(emotions.cortisol - targetCortisol);
      
      const matchScore = 100 - (dopamineDiff + serotoninDiff + cortisolDiff) / 3;
      
      matches.push({
        songKey,
        matchScore: Math.round(matchScore * 10) / 10,
        emotions
      });
    }
    
    return matches.sort((a, b) => b.matchScore - a.matchScore);
  }

  /**
   * Get feature statistics for all cached songs
   */
  getStats() {
    if (this.featureCache.size === 0) {
      return { message: 'No songs analyzed yet' };
    }

    const features = Array.from(this.featureCache.values());
    
    const avg = (arr, key) => {
      const vals = arr.map(f => f.features?.[key]).filter(v => v !== undefined);
      return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
    };

    return {
      totalSongs: features.length,
      spotifyAnalyzed: features.filter(f => f.source === 'spotify').length,
      heuristicAnalyzed: features.filter(f => f.source === 'heuristic').length,
      averages: {
        energy: avg(features, 'energy').toFixed(2),
        valence: avg(features, 'valence').toFixed(2),
        danceability: avg(features, 'danceability').toFixed(2),
        tempo: avg(features, 'tempo').toFixed(0)
      },
      emotionalProfile: {
        avgDopamine: (features.reduce((a, f) => a + (f.emotions?.dopamine || 0), 0) / features.length).toFixed(1),
        avgSerotonin: (features.reduce((a, f) => a + (f.emotions?.serotonin || 0), 0) / features.length).toFixed(1),
        avgCortisol: (features.reduce((a, f) => a + (f.emotions?.cortisol || 0), 0) / features.length).toFixed(1)
      }
    };
  }
}

// CLI interface
if (import.meta.url === `file://${process.argv[1]}`) {
  const analyzer = new AudioAnalyzer();
  await analyzer.init();

  const command = process.argv[2];

  if (command === 'analyze') {
    const song = process.argv[3];
    const artist = process.argv[4] || 'Unknown';
    const analysis = await analyzer.analyzeSong(song, artist);
    console.log(JSON.stringify(analysis, null, 2));
  } else if (command === 'predict') {
    const song = process.argv[3];
    const artist = process.argv[4] || 'Unknown';
    const analysis = await analyzer.analyzeSong(song, artist);
    console.log(`\n🎵 ${analysis.songKey}`);
    console.log(`━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`);
    console.log(`Source: ${analysis.source}`);
    console.log(`\nAudio Features:`);
    console.log(`  Energy: ${(analysis.features.energy * 100).toFixed(0)}%`);
    console.log(`  Valence: ${(analysis.features.valence * 100).toFixed(0)}%`);
    console.log(`  Danceability: ${(analysis.features.danceability * 100).toFixed(0)}%`);
    console.log(`  Tempo: ${analysis.features.tempo} BPM`);
    console.log(`\nPredicted Neurochemistry:`);
    console.log(`  Dopamine: ${analysis.emotions.dopamine.toFixed(1)}%`);
    console.log(`  Serotonin: ${analysis.emotions.serotonin.toFixed(1)}%`);
    console.log(`  Cortisol: ${analysis.emotions.cortisol.toFixed(1)}%`);
    console.log(`\nPrimary Effect: ${analysis.emotions.primaryEffect.toUpperCase()}`);
    console.log(`Intensity: ${(analysis.emotions.intensity * 100).toFixed(0)}%\n`);
  } else if (command === 'stats') {
    const stats = analyzer.getStats();
    console.log(JSON.stringify(stats, null, 2));
  } else if (command === 'find') {
    const targetD = parseFloat(process.argv[3] || '70');
    const targetS = parseFloat(process.argv[4] || '60');
    const targetC = parseFloat(process.argv[5] || '30');
    const matches = analyzer.findSongsForEmotion(targetD, targetS, targetC);
    console.log(JSON.stringify(matches.slice(0, 10), null, 2));
  } else {
    console.log('Audio Analyzer - Music Feature Extraction\n');
    console.log('Usage:');
    console.log('  node audio-analyzer.js analyze <song> <artist>');
    console.log('  node audio-analyzer.js predict <song> <artist>  (pretty print)');
    console.log('  node audio-analyzer.js stats');
    console.log('  node audio-analyzer.js find <dopamine> <serotonin> <cortisol>');
    console.log('\nSpotify API: ' + (analyzer.spotifyAvailable ? 'Configured ✓' : 'Not configured'));
    console.log('Cached songs: ' + analyzer.featureCache.size);
  }
}

export { AudioAnalyzer };
