import React, { useState, useEffect, useRef } from 'react';
import {
    Camera,
    Mic,
    Play,
    ArrowRight,
    User,
    AlertCircle,
    Clock,
    CheckCircle2,
    Activity,
    RotateCcw,
    Video
} from 'lucide-react';

const DUMMY_QUESTIONS = [
    "Can you describe a time you handled a difficult technical challenge?",
    "How do you prioritize your tasks when working on multiple projects?",
    "Tell me about a time you had a conflict with a teammate and how you resolved it.",
    "What is your greatest professional achievement so far?",
    "Where do you see yourself in five years?"
];

const InterViewPage = () => {
    const [step, setStep] = useState(1); // 1: Initial, 2: Setup, 3: Brief, 4: Interview, 5: Processing
    const [currentQ, setCurrentQ] = useState(0);
    const [seconds, setSeconds] = useState(0);
    const [isCameraReady, setIsCameraReady] = useState(false);
    const videoRef = useRef(null);
    const streamRef = useRef(null);

    // --- CAMERA LOGIC ---
    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 1280, height: 720 },
                audio: true
            });
            streamRef.current = stream;
            setIsCameraReady(true);

            // Immediate attachment if ref is available
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
            }
        } catch (err) {
            console.error("Camera Error:", err);
        }
    };

    // IMPORTANT: This effect ensures the video feed re-attaches
    // every time the UI switches between setup and interview steps
    useEffect(() => {
        if (isCameraReady && streamRef.current && videoRef.current) {
            videoRef.current.srcObject = streamRef.current;
        }
    }, [step, isCameraReady]);

    const stopCamera = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
        }
    };

    // --- TIMER LOGIC ---
    useEffect(() => {
        let interval = null;
        if (step === 4) {
            interval = setInterval(() => {
                setSeconds((prev) => prev + 1);
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [step]);

    const formatTime = (totalSeconds) => {
        const mins = Math.floor(totalSeconds / 60);
        const secs = totalSeconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    // --- NAVIGATION ---
    const handleNext = () => {
        if (currentQ < DUMMY_QUESTIONS.length - 1) {
            setCurrentQ(prev => prev + 1);
            // setSeconds(0); // Uncomment if you want to reset timer per question
        } else {
            setStep(5);
            stopCamera();
        }
    };

    // --- COMPONENTS ---
    const LoadingScreen = ({ message }) => (
        <div className="flex flex-col items-center justify-center h-64 space-y-4">
            <div className="relative">
                <div className="w-12 h-12 border-4 border-blue-100 rounded-full"></div>
                <div className="absolute top-0 w-12 h-12 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
            </div>
            <p className="text-gray-500 font-medium animate-pulse">{message}</p>
        </div>
    );

    return (
        <div className="min-h-screen bg-slate-50 font-sans text-slate-900">
            {/* Header */}
            <nav className="bg-white border-b px-6 py-4 flex justify-between items-center sticky top-0 z-50">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold shadow-sm shadow-blue-200">A</div>
                    <span className="text-xl font-black tracking-tighter text-slate-800 uppercase">AceView</span>
                </div>
                <div className="hidden md:flex items-center gap-4 text-sm font-medium text-slate-500">
                    <span>Interview ID: <span className="text-slate-800 font-mono bg-slate-100 px-2 py-1 rounded">#SESS-88219</span></span>
                </div>
            </nav>

            <main className="max-w-6xl mx-auto p-4 md:p-8">

                {/* STEP 1: INITIAL PROCESSING */}
                {step === 1 && (
                    <div className="max-w-md mx-auto mt-20">
                        <div className="bg-white p-8 rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-100 text-center">
                            <LoadingScreen message="Analyzing your resume..." />
                            <button
                                onClick={() => setStep(2)}
                                className="mt-8 w-full bg-slate-900 text-white py-4 rounded-2xl hover:bg-slate-800 transition-all font-bold shadow-lg"
                            >
                                Start Interview Setup
                            </button>
                        </div>
                    </div>
                )}

                {/* STEP 2: CAMERA/MIC SETUP */}
                {step === 2 && (
                    <div className="grid md:grid-cols-2 gap-8 items-start animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-200">
                            <h2 className="text-2xl font-bold mb-2">Check your setup</h2>
                            <p className="text-slate-500 mb-6 text-sm">Make sure you are in a well-lit room and your microphone is working.</p>

                            <div className="relative bg-slate-900 rounded-2xl aspect-video overflow-hidden mb-6 group">
                                <video
                                    ref={videoRef}
                                    autoPlay
                                    muted
                                    playsInline
                                    className="w-full h-full object-cover scale-x-[-1]"
                                />
                                {!isCameraReady && (
                                    <div className="absolute inset-0 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm">
                                        <button onClick={startCamera} className="flex items-center gap-2 bg-white text-slate-900 px-6 py-3 rounded-full font-bold shadow-2xl hover:scale-105 transition-transform">
                                            <Camera size={20} /> Enable Camera
                                        </button>
                                    </div>
                                )}
                                {isCameraReady && (
                                    <div className="absolute top-4 left-4 flex gap-2">
                                        <span className="bg-green-500 text-white px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider">Camera Active</span>
                                    </div>
                                )}
                            </div>

                            <div className="grid grid-cols-2 gap-4 mb-6">
                                <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 flex items-center gap-3">
                                    <div className="w-8 h-8 rounded-full bg-green-100 text-green-600 flex items-center justify-center"><Mic size={16}/></div>
                                    <div><p className="text-[10px] text-slate-500 uppercase font-bold">Audio</p><p className="text-sm font-bold">System OK</p></div>
                                </div>
                                <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 flex items-center gap-3">
                                    <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center"><Video size={16}/></div>
                                    <div><p className="text-[10px] text-slate-500 uppercase font-bold">Video</p><p className="text-sm font-bold">HD Enabled</p></div>
                                </div>
                            </div>

                            <button
                                disabled={!isCameraReady}
                                onClick={() => setStep(3)}
                                className={`w-full py-4 rounded-2xl font-bold transition-all ${isCameraReady ? 'bg-blue-600 text-white shadow-lg shadow-blue-100 hover:bg-blue-700' : 'bg-slate-200 text-slate-400 cursor-not-allowed'}`}
                            >
                                Everything Looks Good
                            </button>
                        </div>

                        <div className="space-y-4">
                            <div className="bg-blue-50 border border-blue-100 p-6 rounded-3xl">
                                <h3 className="font-bold text-blue-900 mb-2 flex items-center gap-2 text-sm"><AlertCircle size={16}/> Pro Tip</h3>
                                <p className="text-blue-800 text-sm leading-relaxed opacity-80">Place your camera at eye level and avoid bright windows directly behind you for the best AI analysis results.</p>
                            </div>
                            <div className="p-6">
                                <h3 className="font-bold mb-4 text-sm uppercase tracking-widest text-slate-400">Required Permissions</h3>
                                <ul className="space-y-4">
                                    <li className="flex items-center gap-3 text-sm font-medium">
                                        <div className={`w-6 h-6 rounded-full flex items-center justify-center ${isCameraReady ? 'bg-green-100 text-green-600' : 'bg-slate-100 text-slate-400'}`}>
                                            {isCameraReady ? <CheckCircle2 size={14}/> : '1'}
                                        </div>
                                        Camera Access
                                    </li>
                                    <li className="flex items-center gap-3 text-sm font-medium text-slate-400">
                                        <div className="w-6 h-6 rounded-full bg-slate-100 flex items-center justify-center">2</div> Microphone Access
                                    </li>
                                    <li className="flex items-center gap-3 text-sm font-medium text-slate-300 italic">
                                        <div className="w-6 h-6 rounded-full bg-slate-50 flex items-center justify-center">3</div> Screen sharing (Optional)
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>
                )}

                {/* STEP 3: PRE-INTERVIEW BRIEF */}
                {step === 3 && (
                    <div className="max-w-2xl mx-auto bg-white rounded-3xl shadow-xl overflow-hidden border border-slate-100 animate-in fade-in zoom-in-95 duration-500">
                        <div className="bg-blue-600 p-8 text-white relative overflow-hidden">
                            <div className="relative z-10">
                                <h2 className="text-3xl font-bold">You're all set!</h2>
                                <p className="opacity-80">Here is what to expect during your AceView session.</p>
                            </div>
                            <Activity size={120} className="absolute -right-8 -bottom-8 opacity-10 text-white" />
                        </div>
                        <div className="p-8 space-y-8">
                            <div className="grid grid-cols-3 gap-4">
                                <div className="text-center p-4 bg-slate-50 rounded-2xl border border-slate-100">
                                    <p className="text-2xl font-bold text-blue-600">{DUMMY_QUESTIONS.length}</p>
                                    <p className="text-[10px] text-slate-500 uppercase font-bold">Questions</p>
                                </div>
                                <div className="text-center p-4 bg-slate-50 rounded-2xl border border-slate-100">
                                    <p className="text-2xl font-bold text-blue-600">~10m</p>
                                    <p className="text-[10px] text-slate-500 uppercase font-bold">Duration</p>
                                </div>
                                <div className="text-center p-4 bg-slate-50 rounded-2xl border border-slate-100">
                                    <p className="text-2xl font-bold text-blue-600">LIVE</p>
                                    <p className="text-[10px] text-slate-500 uppercase font-bold">AI Monitoring</p>
                                </div>
                            </div>

                            <div>
                                <h4 className="font-bold mb-4 flex items-center gap-2 text-sm text-slate-500 uppercase tracking-widest">
                                    <Activity size={16} className="text-blue-600"/> Analysis Parameters
                                </h4>
                                <div className="grid grid-cols-2 gap-3">
                                    {["Eye Contact", "Speech Clarity", "Sentiment", "Posture", "Confidence", "Keyword Usage"].map(item => (
                                        <div key={item} className="flex items-center gap-2 text-sm text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-100/50">
                                            <div className="w-1.5 h-1.5 rounded-full bg-blue-400"></div> {item}
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="bg-amber-50 p-6 rounded-2xl border border-amber-100">
                                <h4 className="font-bold text-amber-900 mb-2 text-sm uppercase tracking-wide">First Question Preview:</h4>
                                <p className="text-amber-800 italic leading-relaxed font-medium">"{DUMMY_QUESTIONS[0]}"</p>
                            </div>

                            <button
                                onClick={() => setStep(4)}
                                className="w-full bg-slate-900 text-white py-5 rounded-2xl font-bold text-lg hover:scale-[1.01] active:scale-95 transition-all flex items-center justify-center gap-2 shadow-xl shadow-slate-200"
                            >
                                Start Interview Now <Play size={20} fill="white"/>
                            </button>
                        </div>
                    </div>
                )}

                {/* STEP 4: MAIN INTERVIEW SCREEN */}
                {step === 4 && (
                    <div className="grid grid-cols-12 gap-6 h-[calc(100vh-180px)] animate-in fade-in duration-700">
                        {/* Left: Video Feed */}
                        <div className="col-span-12 lg:col-span-9 flex flex-col gap-4">
                            <div className="relative flex-1 bg-slate-950 rounded-3xl overflow-hidden shadow-2xl border-4 border-white ring-1 ring-slate-200">
                                {/* THE CAMERA BACKGROUND */}
                                <video
                                    ref={videoRef}
                                    autoPlay
                                    muted
                                    playsInline
                                    className="w-full h-full object-cover scale-x-[-1]"
                                />

                                {/* Overlay: Status Tags */}
                                <div className="absolute top-6 left-6 flex gap-2">
                                    <div className="bg-red-600 text-white px-3 py-1 rounded-full text-[10px] font-black tracking-widest flex items-center gap-2 uppercase shadow-lg">
                                        <div className="w-1.5 h-1.5 bg-white rounded-full animate-ping"></div> Recording
                                    </div>
                                    <div className="bg-black/40 backdrop-blur-md text-white px-3 py-1 rounded-full text-[10px] font-black tracking-widest uppercase border border-white/10">
                                        Live Session
                                    </div>
                                </div>

                                {/* Overlay: Question Text (Transparent background showing camera behind) */}
                                <div className="absolute bottom-0 w-full p-8 bg-gradient-to-t from-black/95 via-black/40 to-transparent">
                                    <div className="max-w-3xl mx-auto">
                                        <p className="text-blue-400 text-xs font-black uppercase tracking-widest mb-2 drop-shadow-md">Question {currentQ + 1} of {DUMMY_QUESTIONS.length}</p>
                                        <p className="text-white text-xl md:text-3xl font-bold leading-tight drop-shadow-lg">
                                            "{DUMMY_QUESTIONS[currentQ]}"
                                        </p>
                                    </div>
                                </div>
                            </div>

                            {/* Controls */}
                            <div className="bg-white p-4 rounded-3xl shadow-sm border border-slate-200 flex justify-between items-center px-8">
                                <div className="flex items-center gap-6">
                                    <div className="flex flex-col">
                                        <span className="text-[10px] uppercase font-black text-slate-400 tracking-wider">Session Time</span>
                                        <span className="text-2xl font-mono font-bold text-slate-800">{formatTime(seconds)}</span>
                                    </div>
                                </div>

                                <div className="flex gap-4">
                                    <button className="p-3 rounded-2xl border border-slate-200 hover:bg-slate-50 text-slate-600 transition-colors">
                                        <RotateCcw size={20} />
                                    </button>
                                    <button
                                        onClick={handleNext}
                                        className="bg-blue-600 hover:bg-blue-700 text-white px-10 py-4 rounded-2xl font-bold flex items-center gap-3 transition-all shadow-lg shadow-blue-200 active:scale-95"
                                    >
                                        {currentQ === DUMMY_QUESTIONS.length - 1 ? 'Finish Interview' : 'Next Question'}
                                        <ArrowRight size={20} />
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Right: AI Sidebar */}
                        <div className="col-span-12 lg:col-span-3 space-y-4">
                            <div className="bg-white p-6 rounded-3xl border border-slate-200 shadow-sm h-full flex flex-col">
                                <h3 className="font-bold flex items-center gap-2 mb-6 text-sm text-slate-500 uppercase tracking-widest">
                                    <Activity size={18} className="text-blue-600"/> AI Live Insights
                                </h3>

                                <div className="space-y-6 flex-1">
                                    <div>
                                        <div className="flex justify-between text-[10px] font-black mb-2 text-slate-400 tracking-widest uppercase"><span>Eye Contact</span><span className="text-blue-600">88%</span></div>
                                        <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                                            <div className="h-full bg-blue-500 transition-all duration-1000" style={{width: '88%'}}></div>
                                        </div>
                                    </div>
                                    <div>
                                        <div className="flex justify-between text-[10px] font-black mb-2 text-slate-400 tracking-widest uppercase"><span>Posture</span><span className="text-green-600">Stable</span></div>
                                        <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                                            <div className="h-full bg-green-500 transition-all duration-1000" style={{width: '95%'}}></div>
                                        </div>
                                    </div>
                                    <div>
                                        <div className="flex justify-between text-[10px] font-black mb-2 text-slate-400 tracking-widest uppercase"><span>Sentiment</span><span className="text-blue-600">Positive</span></div>
                                        <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                                            <div className="h-full bg-blue-500 transition-all duration-1000" style={{width: '72%'}}></div>
                                        </div>
                                    </div>

                                    <div className="pt-6 border-t border-slate-100 space-y-3">
                                        <p className="text-[10px] font-black text-slate-300 uppercase tracking-widest">Live Feedback</p>
                                        <div className="bg-blue-50/50 p-4 rounded-2xl text-[13px] text-blue-800 flex gap-3 border border-blue-100/50 leading-relaxed">
                                            <AlertCircle size={16} className="shrink-0 text-blue-500" />
                                            <span>Try to reduce usage of filler words like "um" and "uh".</span>
                                        </div>
                                        <div className="bg-green-50/50 p-4 rounded-2xl text-[13px] text-green-800 flex gap-3 border border-green-100/50 leading-relaxed">
                                            <CheckCircle2 size={16} className="shrink-0 text-green-500" />
                                            <span>Great eye contact during that last answer!</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* STEP 5: POST-INTERVIEW PROCESSING */}
                {step === 5 && (
                    <div className="max-w-2xl mx-auto mt-16 text-center animate-in fade-in slide-in-from-bottom-10 duration-700">
                        <div className="bg-white p-12 rounded-[3rem] shadow-2xl border border-slate-100">
                            <div className="mb-8 relative inline-block">
                                <div className="w-24 h-24 bg-blue-600 rounded-full flex items-center justify-center text-white shadow-xl shadow-blue-200">
                                    <User size={40} />
                                </div>
                                <div className="absolute -bottom-2 -right-2 w-10 h-10 bg-green-500 rounded-full border-4 border-white flex items-center justify-center text-white shadow-lg">
                                    <CheckCircle2 size={20} />
                                </div>
                            </div>
                            <h2 className="text-4xl font-black mb-4">Interview Complete!</h2>
                            <p className="text-slate-500 mb-8 max-w-sm mx-auto leading-relaxed">
                                We are processing your responses and analyzing your performance metrics. Your final report is being generated.
                            </p>
                            <div className="bg-slate-50 p-6 rounded-3xl border border-slate-100 inline-block w-full">
                                <LoadingScreen message="Compiling behavioral report..." />
                            </div>

                            <div className="mt-12 grid grid-cols-2 gap-4 text-left">
                                <div className="p-5 bg-white rounded-2xl border border-slate-100 shadow-sm">
                                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-1">Answers Recorded</p>
                                    <p className="text-2xl font-bold text-slate-800">5 / 5</p>
                                </div>
                                <div className="p-5 bg-white rounded-2xl border border-slate-100 shadow-sm">
                                    <p className="text-[10px] font-black text-slate-400 uppercase tracking-wider mb-1">Session Duration</p>
                                    <p className="text-2xl font-bold text-slate-800">{formatTime(seconds)}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

            </main>
        </div>
    );
};

export default InterViewPage;