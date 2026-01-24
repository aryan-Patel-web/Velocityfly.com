// import React, { useState, useEffect } from 'react';

// const ViralPixel = () => {
//   // State management
//   const [niches, setNiches] = useState({});
//   const [selectedNiche, setSelectedNiche] = useState(null);
//   const [duration, setDuration] = useState(40);
//   const [voiceStyle, setVoiceStyle] = useState('energetic');
//   const [customTopic, setCustomTopic] = useState('');
//   const [isGenerating, setIsGenerating] = useState(false);
//   const [progress, setProgress] = useState(0);
//   const [currentStep, setCurrentStep] = useState('');
//   const [result, setResult] = useState(null);
//   const [error, setError] = useState(null);
//   const [taskId, setTaskId] = useState(null);

//   // API base URL
//   const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

//   // Load niches on mount
//   useEffect(() => {
//     fetchNiches();
//   }, []);

//   const fetchNiches = async () => {
//     try {
//       const response = await fetch(`${API_BASE}/api/viral-pixel/niches`);
//       const data = await response.json();
//       setNiches(data.niches);
//     } catch (err) {
//       console.error('Failed to load niches:', err);
//     }
//   };

//   // Poll task status
//   useEffect(() => {
//     if (!taskId || !isGenerating) return;

//     const interval = setInterval(async () => {
//       try {
//         const response = await fetch(`${API_BASE}/api/viral-pixel/status/${taskId}`);
//         const data = await response.json();

//         setProgress(data.progress);
//         setCurrentStep(data.step);

//         if (data.status === 'completed') {
//           setResult(data.result);
//           setIsGenerating(false);
//           clearInterval(interval);
//         } else if (data.status === 'failed') {
//           setError(data.error || 'Generation failed');
//           setIsGenerating(false);
//           clearInterval(interval);
//         }
//       } catch (err) {
//         console.error('Status check failed:', err);
//       }
//     }, 2000);

//     return () => clearInterval(interval);
//   }, [taskId, isGenerating]);

//   const generateVideo = async () => {
//     if (!selectedNiche) {
//       setError('Please select a niche');
//       return;
//     }

//     setIsGenerating(true);
//     setProgress(0);
//     setError(null);
//     setResult(null);

//     try {
//       const response = await fetch(`${API_BASE}/api/viral-pixel/generate`, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({
//           niche: selectedNiche,
//           duration: duration,
//           voice_style: voiceStyle,
//           custom_topic: customTopic || null
//         })
//       });

//       if (!response.ok) {
//         throw new Error('Generation failed');
//       }

//       const data = await response.json();
//       setTaskId(data.task_id);

//     } catch (err) {
//       setError(err.message);
//       setIsGenerating(false);
//     }
//   };

//   const downloadVideo = () => {
//     if (result && result.local_path) {
//       window.open(`${API_BASE}/download/${result.local_path}`, '_blank');
//     }
//   };

//   return (
//     <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-black text-white p-6">
//       {/* Header */}
//       <div className="max-w-7xl mx-auto">
//         <div className="text-center mb-12">
//           <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
//             🎬 Viral Video Generator
//           </h1>
//           <p className="text-xl text-gray-300">
//             Create viral YouTube Shorts in minutes using AI + Pexels footage
//           </p>
//         </div>

//         {/* Niche Selection */}
//         <div className="mb-12">
//           <h2 className="text-2xl font-bold mb-6">📋 Step 1: Select Your Niche</h2>
//           <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
//             {Object.entries(niches).map(([key, niche]) => (
//               <div
//                 key={key}
//                 onClick={() => setSelectedNiche(key)}
//                 className={`cursor-pointer p-6 rounded-xl transition-all duration-300 ${
//                   selectedNiche === key
//                     ? 'bg-gradient-to-br from-purple-600 to-pink-600 scale-105 shadow-2xl'
//                     : 'bg-gray-800 hover:bg-gray-700 hover:scale-102'
//                 }`}
//               >
//                 <div className="text-4xl mb-3">{niche.emoji}</div>
//                 <h3 className="text-xl font-bold mb-2">{niche.name}</h3>
//                 <div className="text-sm space-y-1">
//                   <p className="text-gray-300">CPM: {niche.cpm}</p>
//                   <p className="text-green-400">⚡ {niche.viral_potential}</p>
//                 </div>
//               </div>
//             ))}
//           </div>
//         </div>

//         {/* Settings Panel */}
//         {selectedNiche && (
//           <div className="mb-12 bg-gray-800 rounded-xl p-8">
//             <h2 className="text-2xl font-bold mb-6">⚙️ Step 2: Configure Settings</h2>
            
//             <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
//               {/* Duration Slider */}
//               <div>
//                 <label className="block text-lg font-semibold mb-3">
//                   ⏱️ Video Duration: {duration} seconds
//                 </label>
//                 <input
//                   type="range"
//                   min="20"
//                   max="60"
//                   value={duration}
//                   onChange={(e) => setDuration(parseInt(e.target.value))}
//                   className="w-full h-3 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
//                 />
//                 <div className="flex justify-between text-sm text-gray-400 mt-2">
//                   <span>20s (Short)</span>
//                   <span>40s (Optimal)</span>
//                   <span>60s (Long)</span>
//                 </div>
//               </div>

//               {/* Voice Style */}
//               <div>
//                 <label className="block text-lg font-semibold mb-3">
//                   🎙️ Voice Style
//                 </label>
//                 <select
//                   value={voiceStyle}
//                   onChange={(e) => setVoiceStyle(e.target.value)}
//                   className="w-full p-3 bg-gray-700 rounded-lg text-white border border-gray-600 focus:border-purple-500 focus:outline-none"
//                 >
//                   <option value="energetic">Energetic & Exciting</option>
//                   <option value="calm">Calm & Relaxed</option>
//                   <option value="serious">Serious & Professional</option>
//                 </select>
//               </div>
//             </div>

//             {/* Custom Topic */}
//             <div className="mt-6">
//               <label className="block text-lg font-semibold mb-3">
//                 💡 Custom Topic (Optional)
//               </label>
//               <input
//                 type="text"
//                 value={customTopic}
//                 onChange={(e) => setCustomTopic(e.target.value)}
//                 placeholder={`e.g., "${niches[selectedNiche]?.topics[0]}" or leave empty for auto`}
//                 className="w-full p-3 bg-gray-700 rounded-lg text-white border border-gray-600 focus:border-purple-500 focus:outline-none placeholder-gray-400"
//               />
//             </div>
//           </div>
//         )}

//         {/* Generate Button */}
//         {selectedNiche && (
//           <div className="mb-12 text-center">
//             <button
//               onClick={generateVideo}
//               disabled={isGenerating}
//               className={`px-12 py-4 text-xl font-bold rounded-xl transition-all duration-300 ${
//                 isGenerating
//                   ? 'bg-gray-600 cursor-not-allowed'
//                   : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 hover:scale-105 shadow-lg hover:shadow-purple-500/50'
//               }`}
//             >
//               {isGenerating ? (
//                 <span className="flex items-center gap-3">
//                   <svg className="animate-spin h-6 w-6" viewBox="0 0 24 24">
//                     <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
//                     <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
//                   </svg>
//                   Generating... {progress}%
//                 </span>
//               ) : (
//                 '🎬 Generate Viral Video'
//               )}
//             </button>
//           </div>
//         )}

//         {/* Progress Indicator */}
//         {isGenerating && (
//           <div className="mb-12 bg-gray-800 rounded-xl p-8">
//             <h3 className="text-2xl font-bold mb-6">⏳ Generation Progress</h3>
            
//             {/* Progress Bar */}
//             <div className="mb-6">
//               <div className="w-full bg-gray-700 rounded-full h-4 overflow-hidden">
//                 <div
//                   className="bg-gradient-to-r from-purple-500 to-pink-500 h-full transition-all duration-500"
//                   style={{ width: `${progress}%` }}
//                 />
//               </div>
//               <p className="text-center mt-2 text-lg">{progress}%</p>
//             </div>

//             {/* Current Step */}
//             <div className="space-y-3">
//               <div className="flex items-center gap-3 p-3 bg-gray-700 rounded-lg">
//                 <div className="animate-pulse text-2xl">🤖</div>
//                 <div>
//                   <p className="font-semibold">{currentStep}</p>
//                   <p className="text-sm text-gray-400">Please wait, this may take 2-5 minutes...</p>
//                 </div>
//               </div>

//               {/* Progress Steps */}
//               <div className="grid grid-cols-2 md:grid-cols-5 gap-2 mt-4">
//                 {['Script', 'Videos', 'Voice', 'Effects', 'Upload'].map((step, idx) => (
//                   <div
//                     key={step}
//                     className={`p-2 rounded text-center text-sm ${
//                       progress > idx * 20 ? 'bg-purple-600' : 'bg-gray-700'
//                     }`}
//                   >
//                     {step}
//                   </div>
//                 ))}
//               </div>
//             </div>
//           </div>
//         )}

//         {/* Error Display */}
//         {error && (
//           <div className="mb-12 bg-red-900/50 border border-red-500 rounded-xl p-6">
//             <h3 className="text-xl font-bold mb-2">❌ Error</h3>
//             <p className="text-red-200">{error}</p>
//             <button
//               onClick={() => setError(null)}
//               className="mt-4 px-4 py-2 bg-red-700 hover:bg-red-600 rounded-lg"
//             >
//               Dismiss
//             </button>
//           </div>
//         )}

//         {/* Result Display */}
//         {result && (
//           <div className="bg-gradient-to-br from-green-900/50 to-blue-900/50 border border-green-500 rounded-xl p-8">
//             <h2 className="text-3xl font-bold mb-6">✅ Video Generated Successfully!</h2>
            
//             <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
//               {/* Video Info */}
//               <div className="space-y-4">
//                 <div>
//                   <h3 className="text-xl font-semibold mb-2">📺 Title</h3>
//                   <p className="bg-gray-800 p-3 rounded-lg">{result.title}</p>
//                 </div>

//                 <div>
//                   <h3 className="text-xl font-semibold mb-2">🔗 YouTube URL</h3>
//                   <a
//                     href={result.video_url}
//                     target="_blank"
//                     rel="noopener noreferrer"
//                     className="block bg-red-600 hover:bg-red-700 p-3 rounded-lg text-center font-semibold transition-colors"
//                   >
//                     Open on YouTube →
//                   </a>
//                 </div>

//                 <div>
//                   <h3 className="text-xl font-semibold mb-2">🆔 Video ID</h3>
//                   <p className="bg-gray-800 p-3 rounded-lg font-mono text-sm">{result.video_id}</p>
//                 </div>
//               </div>

//               {/* Actions */}
//               <div className="space-y-4">
//                 <h3 className="text-xl font-semibold mb-2">🎯 Actions</h3>
                
//                 <button
//                   onClick={() => window.open(result.video_url, '_blank')}
//                   className="w-full bg-blue-600 hover:bg-blue-700 p-4 rounded-lg font-semibold transition-colors"
//                 >
//                   📺 Watch on YouTube
//                 </button>

//                 <button
//                   onClick={() => {
//                     navigator.clipboard.writeText(result.video_url);
//                     alert('URL copied to clipboard!');
//                   }}
//                   className="w-full bg-purple-600 hover:bg-purple-700 p-4 rounded-lg font-semibold transition-colors"
//                 >
//                   📋 Copy URL
//                 </button>

//                 <button
//                   onClick={() => {
//                     const text = `Check out this amazing video!\n${result.video_url}`;
//                     window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`, '_blank');
//                   }}
//                   className="w-full bg-sky-600 hover:bg-sky-700 p-4 rounded-lg font-semibold transition-colors"
//                 >
//                   🐦 Share on Twitter
//                 </button>

//                 <button
//                   onClick={() => {
//                     setResult(null);
//                     setProgress(0);
//                     setCurrentStep('');
//                   }}
//                   className="w-full bg-green-600 hover:bg-green-700 p-4 rounded-lg font-semibold transition-colors"
//                 >
//                   ✨ Create Another Video
//                 </button>
//               </div>
//             </div>

//             {/* Script Preview */}
//             {result.script && (
//               <div className="mt-6">
//                 <h3 className="text-xl font-semibold mb-3">📝 Script Preview</h3>
//                 <div className="bg-gray-800 p-4 rounded-lg max-h-64 overflow-y-auto">
//                   <p className="text-sm text-gray-300 mb-3">{result.script.description}</p>
//                   <div className="space-y-2">
//                     {result.script.segments?.slice(0, 3).map((seg, idx) => (
//                       <div key={idx} className="border-l-4 border-purple-500 pl-3">
//                         <p className="font-semibold">{seg.text_overlay} {seg.emoji}</p>
//                         <p className="text-sm text-gray-400">{seg.narration}</p>
//                       </div>
//                     ))}
//                   </div>
//                 </div>
//               </div>
//             )}
//           </div>
//         )}

//         {/* Info Section */}
//         {!isGenerating && !result && (
//           <div className="mt-12 bg-gray-800/50 rounded-xl p-8">
//             <h3 className="text-2xl font-bold mb-4">💡 How It Works</h3>
//             <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
//               <div className="text-center">
//                 <div className="text-4xl mb-3">🤖</div>
//                 <h4 className="font-bold mb-2">AI Script Generation</h4>
//                 <p className="text-sm text-gray-400">
//                   AI creates viral scripts with hooks, facts, and engaging narration
//                 </p>
//               </div>
//               <div className="text-center">
//                 <div className="text-4xl mb-3">🎥</div>
//                 <h4 className="font-bold mb-2">Pexels Videos</h4>
//                 <p className="text-sm text-gray-400">
//                   Downloads copyright-free HD videos and extracts best moments
//                 </p>
//               </div>
//               <div className="text-center">
//                 <div className="text-4xl mb-3">✨</div>
//                 <h4 className="font-bold mb-2">Auto Assembly</h4>
//                 <p className="text-sm text-gray-400">
//                   Adds voiceover, text, effects, and uploads to YouTube automatically
//                 </p>
//               </div>
//             </div>

//             <div className="mt-8 p-4 bg-blue-900/30 rounded-lg border border-blue-500">
//               <h4 className="font-bold mb-2">⚡ Why This Works:</h4>
//               <ul className="text-sm text-gray-300 space-y-1">
//                 <li>✅ 100% copyright-free content from Pexels</li>
//                 <li>✅ AI-powered scripts optimized for virality</li>
//                 <li>✅ Professional effects and transitions</li>
//                 <li>✅ Direct upload to YouTube Shorts</li>
//                 <li>✅ High CPM niches ($4-12 per 1000 views)</li>
//                 <li>✅ Channels using this method earn $10K-100K/month</li>
//               </ul>
//             </div>
//           </div>
//         )}

//         {/* Selected Niche Info */}
//         {selectedNiche && niches[selectedNiche] && !result && (
//           <div className="mt-8 bg-gradient-to-r from-purple-900/50 to-pink-900/50 rounded-xl p-6 border border-purple-500">
//             <h3 className="text-xl font-bold mb-3">
//               {niches[selectedNiche].emoji} Selected: {niches[selectedNiche].name}
//             </h3>
//             <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
//               <div>
//                 <p className="text-gray-400">CPM Range</p>
//                 <p className="text-lg font-bold text-green-400">{niches[selectedNiche].cpm}</p>
//               </div>
//               <div>
//                 <p className="text-gray-400">Viral Potential</p>
//                 <p className="text-lg font-bold text-yellow-400">{niches[selectedNiche].viral_potential}</p>
//               </div>
//               <div>
//                 <p className="text-gray-400">Example Topics</p>
//                 <p className="text-sm">{niches[selectedNiche].topics[0]}</p>
//               </div>
//             </div>
//           </div>
//         )}
//       </div>
//     </div>
//   );
// };

// export default ViralPixel;