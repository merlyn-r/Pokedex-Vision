import 'dart:convert';
import 'dart:io';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

const apiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'http://10.0.2.2:5001',
);

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final cameras = await availableCameras();
  runApp(VisionPokedex(cameras: cameras));
}

class VisionPokedex extends StatelessWidget {
  const VisionPokedex({super.key, required this.cameras});
  final List<CameraDescription> cameras;

  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Vision Pokédex',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xffe9414b)),
          useMaterial3: true,
        ),
        home: CameraScreen(cameras: cameras),
      );
}

class CameraScreen extends StatefulWidget {
  const CameraScreen({super.key, required this.cameras});
  final List<CameraDescription> cameras;

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  CameraController? controller;
  bool identifying = false;
  String? error;

  @override
  void initState() {
    super.initState();
    if (widget.cameras.isNotEmpty) {
      controller = CameraController(widget.cameras.first, ResolutionPreset.medium, enableAudio: false);
      controller!.initialize().then((_) => mounted ? setState(() {}) : null).catchError((_) {
        if (mounted) setState(() => error = 'Camera permission was not granted.');
      });
    }
  }

  @override
  void dispose() {
    controller?.dispose();
    super.dispose();
  }

  Future<void> identify() async {
    final camera = controller;
    if (camera == null || !camera.value.isInitialized || identifying) return;
    setState(() {
      identifying = true;
      error = null;
    });
    try {
      final frame = await camera.takePicture();
      final request = http.MultipartRequest('POST', Uri.parse('$apiBaseUrl/api/identify'));
      request.files.add(await http.MultipartFile.fromPath('image', frame.path));
      final response = await http.Response.fromStream(await request.send());

      debugPrint('========== POKEDEX DEBUG ==========');
      debugPrint('STATUS: ${response.statusCode}');
      debugPrint('BODY: ${response.body}');
      debugPrint('===================================');

      final payload = jsonDecode(response.body) as Map<String, dynamic>;
      if (response.statusCode >= 400) throw Exception(payload['error'] ?? 'Identification failed.');
      if (!mounted) return;
      await Navigator.push(context, MaterialPageRoute(builder: (_) => DetailScreen(payload: payload, photo: frame)));
    } catch (exception) {
      if (mounted) setState(() => error = 'Could not identify this Pokémon. ${exception.toString().replaceFirst('Exception: ', '')}');
    } finally {
      if (mounted) setState(() => identifying = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final camera = controller;
    return Scaffold(
      appBar: AppBar(title: const Text('VISION POKÉDEX')),
      body: camera == null
          ? const Center(child: Text('No camera is available.'))
          : !camera.value.isInitialized
              ? const Center(child: CircularProgressIndicator())
              : Stack(fit: StackFit.expand, children: [
                  CameraPreview(camera),
                  const Center(child: _TargetFrame()),
                  if (error != null) Positioned(left: 16, right: 16, bottom: 115, child: _Message(text: error!)),
                ]),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
      floatingActionButton: FloatingActionButton.extended(
        onPressed: identifying ? null : identify,
        icon: identifying ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.center_focus_strong),
        label: Text(identifying ? 'Identifying…' : 'Identify Pokémon'),
      ),
    );
  }
}

class DetailScreen extends StatelessWidget {
  const DetailScreen({super.key, required this.payload, required this.photo});
  final Map<String, dynamic> payload;
  final XFile photo;

  @override
  Widget build(BuildContext context) {
    final pokemon = payload['pokemon'] as Map<String, dynamic>;
    final predictions = (payload['predictions'] as List).cast<Map<String, dynamic>>();
    final types = (pokemon['types'] as List).whereType<String>().toList();
    final stats = (pokemon['stats'] as List).cast<List>();
    final evolution = (pokemon['evolution'] as List).cast<Map<String, dynamic>>();
    final moves = (pokemon['moves'] as List).cast<Map<String, dynamic>>();
    return Scaffold(
      appBar: AppBar(title: Text('#${pokemon['dex_id']} ${pokemon['name']}')),
      body: ListView(padding: const EdgeInsets.all(20), children: [
        Center(child: ClipRRect(borderRadius: BorderRadius.circular(18), child: Image.file(File(photo.path), height: 190, fit: BoxFit.cover))),
        const SizedBox(height: 16),
        Text(pokemon['name'], style: Theme.of(context).textTheme.displaySmall?.copyWith(fontWeight: FontWeight.bold)),
        Text(pokemon['category'] as String),
        const SizedBox(height: 8),
        Wrap(spacing: 8, children: types.map((type) => Chip(label: Text(type))).toList()),
        Text(pokemon['flavor'] as String, style: const TextStyle(height: 1.45)),
        _Section('Vision result', [Text('Confidence: ${predictions.first['confidence']}%'), Text('Other guesses: ${predictions.skip(1).map((p) => p['name']).join(', ')}')]),
        _Section('Profile', [Text('Height: ${pokemon['height']}  ·  Weight: ${pokemon['weight']}'), Text('Abilities: ${(pokemon['abilities'] as List).join(', ')}')]),
        _Section('Base stats · ${pokemon['total']}', stats.map((stat) => _Stat(label: stat[0].toString(), value: int.parse(stat[1].toString()))).toList()),
        _Section('Evolution line', [Text(evolution.map((item) => '#${item['dex_id']} ${item['name']}').join('  →  '))]),
        _Section('Moveset', moves.map((move) => ListTile(contentPadding: EdgeInsets.zero, title: Text(move['name'] as String), subtitle: Text('${move['type']} · Power ${move['power']} · ${move['level']}'))).toList()),
      ]),
    );
  }
}

class _Section extends StatelessWidget {
  const _Section(this.title, this.children);
  final String title;
  final List<Widget> children;
  @override
  Widget build(BuildContext context) => Card(margin: const EdgeInsets.only(top: 18), child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(title, style: Theme.of(context).textTheme.titleLarge), const SizedBox(height: 8), ...children])));
}

class _Stat extends StatelessWidget {
  const _Stat({required this.label, required this.value});
  final String label;
  final int value;
  @override
  Widget build(BuildContext context) => Row(children: [SizedBox(width: 62, child: Text(label)), Expanded(child: LinearProgressIndicator(value: value / 180)), const SizedBox(width: 8), Text('$value')]);
}

class _TargetFrame extends StatelessWidget {
  const _TargetFrame();
  @override
  Widget build(BuildContext context) => Container(width: 260, height: 260, decoration: BoxDecoration(border: Border.all(color: Colors.white, width: 3), borderRadius: BorderRadius.circular(24)));
}

class _Message extends StatelessWidget {
  const _Message({required this.text});
  final String text;
  @override
  Widget build(BuildContext context) => Card(color: Colors.white, child: Padding(padding: const EdgeInsets.all(12), child: Text(text)));
}
