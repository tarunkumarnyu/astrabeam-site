// Video helper for the site. macOS only, no ffmpeg needed (uses AVFoundation).
//
//   swift tools/video.swift info   IN.mp4
//   swift tools/video.swift frames IN.mp4 OUT_DIR [COUNT=12] [WIDTH=960]
//   swift tools/video.swift poster IN.mp4 OUT.jpg [SECONDS=0.3]
//   swift tools/video.swift encode IN.mp4 OUT.mp4 WIDTH HEIGHT BITRATE [--keep-audio]
//   swift tools/video.swift sequence FRAME_DIR OUT.mp4 FPS BITRATE   (JPEGs, sorted by name)
//
// `encode` writes web-friendly H.264 (fast-start, keyframe every 2 s). Audio is
// dropped unless --keep-audio is given; background videos play muted anyway.
import AVFoundation
import AppKit

let args = CommandLine.arguments
func fail(_ msg: String) -> Never { FileHandle.standardError.write((msg + "\n").data(using: .utf8)!); exit(1) }
guard args.count >= 3 else { fail("usage: video.swift info|frames|poster|encode|sequence IN ...") }

if args[1] == "sequence" {
  guard args.count >= 6 else { fail("sequence FRAME_DIR OUT.mp4 FPS BITRATE") }
  let dir = URL(fileURLWithPath: args[2]), dst = URL(fileURLWithPath: args[3])
  let fps = Int32(args[4])!, bps = Int(args[5])!
  let files = try! FileManager.default.contentsOfDirectory(atPath: dir.path).filter { $0.lowercased().hasSuffix(".jpg") }.sorted()
  guard !files.isEmpty else { fail("no .jpg frames in \(dir.path)") }
  func load(_ f: String) -> CGImage { NSImage(contentsOf: dir.appendingPathComponent(f))!.cgImage(forProposedRect: nil, context: nil, hints: nil)! }
  let first = load(files[0]); let W = first.width, H = first.height
  try? FileManager.default.removeItem(at: dst)
  let w = try! AVAssetWriter(outputURL: dst, fileType: .mp4); w.shouldOptimizeForNetworkUse = true
  let inp = AVAssetWriterInput(mediaType: .video, outputSettings: [AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: W, AVVideoHeightKey: H,
    AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: bps, AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel, AVVideoMaxKeyFrameIntervalKey: Int(fps)]])
  let ad = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: inp, sourcePixelBufferAttributes: [
    kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32ARGB, kCVPixelBufferWidthKey as String: W, kCVPixelBufferHeightKey as String: H])
  w.add(inp); w.startWriting(); w.startSession(atSourceTime: .zero)
  for (i, f) in files.enumerated() {
    while !inp.isReadyForMoreMediaData { usleep(2000) }
    var pb: CVPixelBuffer?; CVPixelBufferPoolCreatePixelBuffer(nil, ad.pixelBufferPool!, &pb)
    CVPixelBufferLockBaseAddress(pb!, [])
    let ctx = CGContext(data: CVPixelBufferGetBaseAddress(pb!), width: W, height: H, bitsPerComponent: 8,
                        bytesPerRow: CVPixelBufferGetBytesPerRow(pb!), space: CGColorSpaceCreateDeviceRGB(),
                        bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue)!
    ctx.draw(load(f), in: CGRect(x: 0, y: 0, width: W, height: H))
    CVPixelBufferUnlockBaseAddress(pb!, [])
    ad.append(pb!, withPresentationTime: CMTime(value: CMTimeValue(i), timescale: fps))
  }
  inp.markAsFinished(); let sem = DispatchSemaphore(value: 0); w.finishWriting { sem.signal() }; sem.wait()
  guard w.status == .completed else { fail("sequence failed: \(String(describing: w.error))") }
  let outDir = dst.deletingLastPathComponent().path
  for f in (try? FileManager.default.contentsOfDirectory(atPath: outDir)) ?? []
  where f.hasPrefix(dst.lastPathComponent + ".sb-") { try? FileManager.default.removeItem(atPath: outDir + "/" + f) }
  print("ok  \(files.count) frames  \(W)x\(H)  -> \(dst.lastPathComponent)")
  exit(0)
}

let src = URL(fileURLWithPath: args[2])
let asset = AVURLAsset(url: src)
let duration = CMTimeGetSeconds(asset.duration)

func writeJPEG(_ cg: CGImage, _ path: String, quality: Double = 0.8) {
  let data = NSBitmapImageRep(cgImage: cg).representation(using: .jpeg, properties: [.compressionFactor: quality])!
  try! data.write(to: URL(fileURLWithPath: path))
}

func generator(maxWidth: Int? = nil) -> AVAssetImageGenerator {
  let g = AVAssetImageGenerator(asset: asset)
  g.appliesPreferredTrackTransform = true
  g.requestedTimeToleranceBefore = .zero
  g.requestedTimeToleranceAfter = .zero
  if let w = maxWidth { g.maximumSize = CGSize(width: w, height: w) }
  return g
}

switch args[1] {
case "info":
  print(String(format: "duration %.2f s", duration))
  for t in asset.tracks {
    let size = t.naturalSize.applying(t.preferredTransform)
    print(t.mediaType.rawValue, "\(Int(abs(size.width)))x\(Int(abs(size.height)))",
          String(format: "%.2f fps  %.2f Mbps", t.nominalFrameRate, t.estimatedDataRate / 1e6))
  }

case "frames":
  guard args.count >= 4 else { fail("frames IN OUT_DIR [COUNT] [WIDTH]") }
  let count = args.count > 4 ? Int(args[4])! : 12
  let g = generator(maxWidth: args.count > 5 ? Int(args[5])! : 960)
  try? FileManager.default.createDirectory(atPath: args[3], withIntermediateDirectories: true)
  for i in 0..<count {
    let t = duration * (Double(i) + 0.5) / Double(count)
    if let cg = try? g.copyCGImage(at: CMTime(seconds: t, preferredTimescale: 600), actualTime: nil) {
      writeJPEG(cg, "\(args[3])/f\(String(format: "%02d", i)).jpg")
      print(String(format: "f%02d  t=%.2f s", i, t))
    }
  }

case "poster":
  guard args.count >= 4 else { fail("poster IN OUT.jpg [SECONDS]") }
  let t = args.count > 4 ? Double(args[4])! : 0.3
  let cg = try! generator().copyCGImage(at: CMTime(seconds: t, preferredTimescale: 600), actualTime: nil)
  writeJPEG(cg, args[3], quality: 0.72)
  print("poster \(cg.width)x\(cg.height) at \(t) s")

case "encode":
  guard args.count >= 7 else { fail("encode IN OUT W H BITRATE [--keep-audio]") }
  let dst = URL(fileURLWithPath: args[3])
  let W = Int(args[4])!, H = Int(args[5])!, bps = Int(args[6])!
  let keepAudio = args.contains("--keep-audio")
  try? FileManager.default.removeItem(at: dst)
  let vtrack = asset.tracks(withMediaType: .video)[0]
  let reader = try! AVAssetReader(asset: asset)
  let vout = AVAssetReaderTrackOutput(track: vtrack, outputSettings: [
    kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_420YpCbCr8BiPlanarVideoRange])
  reader.add(vout)
  let writer = try! AVAssetWriter(outputURL: dst, fileType: .mp4)
  writer.shouldOptimizeForNetworkUse = true
  let fps = max(1, Int(vtrack.nominalFrameRate.rounded()))
  let vin = AVAssetWriterInput(mediaType: .video, outputSettings: [
    AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: W, AVVideoHeightKey: H,
    AVVideoScalingModeKey: AVVideoScalingModeResizeAspectFill,
    AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: bps,
                                      AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel,
                                      AVVideoMaxKeyFrameIntervalKey: fps * 2]])
  vin.transform = vtrack.preferredTransform
  writer.add(vin)
  var aout: AVAssetReaderTrackOutput? = nil, ain: AVAssetWriterInput? = nil
  if keepAudio, let atrack = asset.tracks(withMediaType: .audio).first {
    aout = AVAssetReaderTrackOutput(track: atrack, outputSettings: [AVFormatIDKey: kAudioFormatLinearPCM])
    reader.add(aout!)
    ain = AVAssetWriterInput(mediaType: .audio, outputSettings: [
      AVFormatIDKey: kAudioFormatMPEG4AAC, AVNumberOfChannelsKey: 2, AVSampleRateKey: 48000, AVEncoderBitRateKey: 128000])
    writer.add(ain!)
  }
  reader.startReading(); writer.startWriting(); writer.startSession(atSourceTime: .zero)
  let group = DispatchGroup()
  func pump(_ input: AVAssetWriterInput, _ output: AVAssetReaderTrackOutput, _ label: String) {
    group.enter()
    input.requestMediaDataWhenReady(on: DispatchQueue(label: label)) {
      while input.isReadyForMoreMediaData {
        if let sb = output.copyNextSampleBuffer() { input.append(sb) } else { input.markAsFinished(); group.leave(); return }
      }
    }
  }
  pump(vin, vout, "video")
  if let ain = ain, let aout = aout { pump(ain, aout, "audio") }
  group.wait()
  let done = DispatchSemaphore(value: 0)
  writer.finishWriting { done.signal() }
  done.wait()
  guard writer.status == .completed else { fail("encode failed: \(String(describing: writer.error))") }
  // AVAssetWriter can leave sandbox temp files (OUT.sb-*) next to the output.
  let dir = dst.deletingLastPathComponent().path
  for f in (try? FileManager.default.contentsOfDirectory(atPath: dir)) ?? []
  where f.hasPrefix(dst.lastPathComponent + ".sb-") { try? FileManager.default.removeItem(atPath: dir + "/" + f) }
  let size = (try! FileManager.default.attributesOfItem(atPath: dst.path)[.size] as! Int)
  print(String(format: "ok  %@  %.1f MB", dst.lastPathComponent, Double(size) / 1e6))

default:
  fail("unknown command \(args[1])")
}
