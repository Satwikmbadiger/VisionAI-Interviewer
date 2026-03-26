import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useParams } from 'react-router-dom';
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

const InterViewPage = () => {
    // --- ROUTER STATE ---
    const { id } = useParams(); 
    const location = useLocation(); 
    const questions = location.state?.questions || [];

    // --- COMPONENT STATE ---
    const [step, setStep] = useState(1);
    const [currentQ, setCurrentQ] = useState(0);
    const [seconds, setSeconds] = useState(0);
    const [isCameraReady, setIsCameraReady] = useState(false);
    
    // --- REFS ---
    const videoRef = useRef(null);
    const streamRef = useRef(null);
    const mediaRecorderRef = useRef(null);
    const recordedChunksRef = useRef([]);
    const currentQuestionRef = useRef(0); // Keeps track of question index safely for the recorder

    // Keep the ref synced with state so the recorder always knows what it's recording
    useEffect(() => {
        currentQuestionRef.current = currentQ;
    }, [currentQ]);

    // --- CAMERA LOGIC ---
    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { width: 1280, height: 720 },
                audio: true
            });
            streamRef.current = stream;
            setIsCameraReady(true);

            if (videoRef.current) {
                videoRef.current.srcObject = stream;
            }
        } catch (err) {
            console.error("Camera Error:", err);
        }
    };

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

    // --- RECORDING LOGIC (PER-QUESTION CHUNKING) ---
    const startRecording = () => {
        if (!streamRef.current) return;
        
        recordedChunksRef.current = []; 
        
        // Check for browser codec support
        let options = { mimeType: 'video/webm' };
        if (MediaRecorder.isTypeSupported('video/webm;codecs=vp8,opus')) {
            options = { mimeType: 'video/webm;codecs=vp8,opus' };
        }

        mediaRecorderRef.current = new MediaRecorder(streamRef.current, options);

        mediaRecorderRef.current.ondataavailable = (event) => {
            if (event.data && event.data.size > 0) {
                recordedChunksRef.current.push(event.data);
            }
        };

        // Capture the EXACT question index at the moment this recording started
        const qIndexAtStart = currentQuestionRef.current;
        const qData = questions[qIndexAtStart];

        mediaRecorderRef.current.onstop = () => {
            const blob = new Blob(recordedChunksRef.current, { type: 'video/webm' });
            uploadAnswerChunk(blob, qData, qIndexAtStart);
        };

        mediaRecorderRef.current.start();
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
            mediaRecorderRef.current.stop();
        }
    };

    const uploadAnswerChunk = async (blob, questionData, index) => {
        const formData = new FormData();
        
        // Give the file a clean name: "q0_session123.webm"
        formData.append('video', blob, `q${index}_session${id}.webm`);
        
        // Pass the actual DB ID of the question if it exists, otherwise pass the index
        formData.append('question_id', questionData?.id || index);
        formData.append('session_id', id);

        try {
            console.log(`[⬆️] Uploading answer for Question ${index + 1}...`);
            const response = await fetch('http://localhost:8080/api/interview/upload-answer', {
                method: 'POST',
                body: formData,
            });
            
            if (response.ok) {
                console.log(`[✅] Question ${index + 1} uploaded successfully!`);
            } else {
                console.error(`[❌] Server rejected Question ${index + 1}`);
            }
        } catch (error) {
            console.error(`[❌] Failed to upload Question ${index + 1}:`, error);
        }
    };

    // --- TIMER & INITIALIZATION LOGIC ---
    useEffect(() => {
        let interval = null;
        if (step === 4) {
            // Start the timer
            interval = setInterval(() => {
                setSeconds((prev) => prev + 1);
            }, 1000);
            
            // Start recording Question 1 immediately when the interview step loads
            startRecording();
        }
        
        return () => {
            clearInterval(interval);
            // Safety cleanup: stop recording if component unmounts unexpectedly
            if (step === 4) stopRecording();
        };
    }, [step]);

    const formatTime = (totalSeconds) => {
        const mins = Math.floor(totalSeconds / 60);
        const secs = totalSeconds % 60;
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    // --- NAVIGATION ---
    const handleNext = () => {
        // 1. Stop the current recording (this automatically triggers the upload!)
        stopRecording();

        if (currentQ < questions.length - 1) {
            // 2. Move UI to the next question
            setCurrentQ(prev => prev + 1);
            
            // 3. Start a fresh recording after a tiny delay so the previous blob can finalize
            setTimeout(() => {
                startRecording();
            }, 500);
            
        } else {
            // Finish Interview
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

    if (!questions || questions.length === 0) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-slate-50">
                <div className="text-center p-8 bg-white rounded-xl shadow-sm border border-slate-200">
                    <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                    <h2 className="text-xl font-bold mb-2">Session Data Missing</h2>
                    <p className="text-slate-500">Please start the interview from the main setup page.</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-50 font-sans text-slate-900">
            {/* Header */}
            <nav className="bg-white border-b px-6 py-4 flex justify-between items-center sticky top-0 z-50">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold shadow-sm shadow-blue-200">A</div>
                    <span className="text-xl font-black tracking-tighter text-slate-800 uppercase">AceView</span>
                </div>
                <div className="hidden md:flex items-center gap-4 text-sm font-medium text-slate-500">
                    <span>Interview ID: <span className="text-slate-800 font-mono bg-slate-100 px-2 py-1 rounded">#{id?.slice(0, 8)}</span></span>
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
                                <video ref={videoRef} autoPlay muted playsInline className="w-full h-full object-cover scale-x-[-1]" />
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
                                    <p className="text-2xl font-bold text-blue-600">{questions.length}</p>
                                    <p className="text-[10px] text-slate-500 uppercase font-bold">Questions</p>
                                </div>
                                <div className="text-center p-4 bg-slate-50 rounded-2xl border border-slate-100">
                                    <p className="text-2xl font-bold text-blue-600">~{questions.length * 2}m</p>
                                    <p className="text-[10px] text-slate-500 uppercase font-bold">Duration</p>
                                </div>
                                <div className="text-center p-4 bg-slate-50 rounded-2xl border border-slate-100">
                                    <p className="text-2xl font-bold text-blue-600">LIVE</p>
                                    <p className="text-[10px] text-slate-500 uppercase font-bold">AI Monitoring</p>
                                </div>
                            </div>

                            <div className="bg-amber-50 p-6 rounded-2xl border border-amber-100">
                                <h4 className="font-bold text-amber-900 mb-2 text-sm uppercase tracking-wide">First Question Preview:</h4>
                                <p className="text-amber-800 italic leading-relaxed font-medium">"{questions[0]?.question}"</p>
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
                                <video ref={videoRef} autoPlay muted playsInline className="w-full h-full object-cover scale-x-[-1]" />

                                {/* Overlay: Status Tags */}
                                <div className="absolute top-6 left-6 flex gap-2">
                                    <div className="bg-red-600 text-white px-3 py-1 rounded-full text-[10px] font-black tracking-widest flex items-center gap-2 uppercase shadow-lg">
                                        <div className="w-1.5 h-1.5 bg-white rounded-full animate-ping"></div> Recording Answer
                                    </div>
                                </div>

                                {/* Overlay: Question Text */}
                                <div className="absolute bottom-0 w-full p-8 bg-gradient-to-t from-black/95 via-black/40 to-transparent">
                                    <div className="max-w-3xl mx-auto">
                                        <div className="flex items-center gap-3 mb-2">
                                            <p className="text-blue-400 text-xs font-black uppercase tracking-widest drop-shadow-md">
                                                Question {currentQ + 1} of {questions.length}
                                            </p>
                                            <span className="bg-blue-900/50 text-blue-200 text-[10px] uppercase font-bold px-2 py-0.5 rounded border border-blue-500/30">
                                                {questions[currentQ]?.type || "General"}
                                            </span>
                                        </div>
                                        <p className="text-white text-xl md:text-3xl font-bold leading-tight drop-shadow-lg">
                                            "{questions[currentQ]?.question}"
                                        </p>
                                    </div>
                                </div>
                            </div>

                            {/* Controls */}
                            <div className="bg-white p-4 rounded-3xl shadow-sm border border-slate-200 flex justify-between items-center px-8">
                                <div className="flex flex-col">
                                    <span className="text-[10px] uppercase font-black text-slate-400 tracking-wider">Session Time</span>
                                    <span className="text-2xl font-mono font-bold text-slate-800">{formatTime(seconds)}</span>
                                </div>

                                <div className="flex gap-4">
                                    <button
                                        onClick={handleNext}
                                        className="bg-blue-600 hover:bg-blue-700 text-white px-10 py-4 rounded-2xl font-bold flex items-center gap-3 transition-all shadow-lg shadow-blue-200 active:scale-95"
                                    >
                                        {currentQ === questions.length - 1 ? 'Finish Interview' : 'Next Question'}
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
                                    <div className="bg-blue-50/50 p-4 rounded-2xl text-[13px] text-blue-800 flex gap-3 border border-blue-100/50 leading-relaxed">
                                        <Activity size={16} className="shrink-0 text-blue-500" />
                                        <span>Recording in progress. Insights will be generated after the session.</span>
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
                                    <CheckCircle2 size={40} />
                                </div>
                            </div>
                            <h2 className="text-4xl font-black mb-4">Interview Complete!</h2>
                            <p className="text-slate-500 mb-8 max-w-sm mx-auto leading-relaxed">
                                Your answers have been uploaded and are being processed by the AI.
                            </p>
                            <div className="bg-slate-50 p-6 rounded-3xl border border-slate-100 inline-block w-full">
                                <LoadingScreen message="Compiling your performance report..." />
                            </div>
                        </div>
                    </div>
                )}

            </main>
        </div>
    );
};

export default InterViewPage;