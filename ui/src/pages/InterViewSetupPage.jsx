import React, { useState } from 'react';
import {useNavigate} from "react-router-dom";
import { Upload, FileText, Briefcase, CheckCircle, Settings, Clock, MessageSquare, Video, Users } from 'lucide-react';

const InterviewSetupPage = () => {
    const [documentChoice, setDocumentChoice] = useState('both');
    const [uploadedResume, setUploadedResume] = useState(null);
    const [uploadedJD, setUploadedJD] = useState(null);
    const [interviewSettings, setInterviewSettings] = useState({
        duration: '30',
        difficulty: 'medium',
        focusArea: 'balanced',
        questionCount: '5',
        includeVideo: true,
        includeBehavioral: true
    });
    const navigate = useNavigate();

    const handleFileUpload = (e, type) => {
        const file = e.target.files[0];
        if (file) {
            if (type === 'resume') {
                setUploadedResume(file);
            } else {
                setUploadedJD(file);
            }
        }
    };

    const canStartInterview = () => {
        if (documentChoice === 'both') {
            return uploadedResume && uploadedJD;
        } else if (documentChoice === 'resume') {
            return uploadedResume;
        } else if (documentChoice === 'jd') {
            return uploadedJD;
        }
        return false;
    };

    const handleStartInterview = () => {
        if (!canStartInterview()) {
            alert("Please upload the required document(s) to continue.");
            return;
        }
        console.log("Starting interview with settings:", interviewSettings);
        console.log("Document choice:", documentChoice);
        alert("Interview would start now with your custom settings!");
        navigate("/Interview/sessionId");


    };

    return (
        <div className="min-h-screen bg-slate-950 text-white p-8">
            <div className="max-w-5xl mx-auto">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold mb-3 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                        Setup Your AI Interview
                    </h1>
                    <p className="text-slate-300 text-lg">
                        Upload your documents and customize your practice session
                    </p>
                </div>

                {/* Document Upload Section */}
                <div className="bg-slate-900/80 backdrop-blur rounded-2xl border border-slate-800 p-8 mb-6 shadow-xl">
                    <h2 className="text-2xl font-semibold mb-6 flex items-center gap-2">
                        <Upload className="w-6 h-6 text-blue-400" />
                        Upload Documents
                    </h2>

                    {/* Document Choice Selection */}
                    <div className="mb-8">
                        <label className="text-sm font-medium mb-3 block text-slate-400">
                            Choose what to upload:
                        </label>
                        <div className="grid grid-cols-3 gap-4">
                            <button
                                onClick={() => setDocumentChoice('resume')}
                                className={`p-4 rounded-lg border-2 transition-all ${
                                    documentChoice === 'resume'
                                        ? 'border-blue-500 bg-blue-500/10 text-white shadow-lg shadow-blue-500/20'
                                        : 'border-slate-800 bg-slate-900/50 text-slate-400 hover:border-slate-700 hover:bg-slate-900/80'
                                }`}
                            >
                                <FileText className="w-6 h-6 mx-auto mb-2" />
                                <p className="font-semibold text-sm">Resume Only</p>
                                <p className="text-xs text-slate-500 mt-1">General practice</p>
                            </button>

                            <button
                                onClick={() => setDocumentChoice('jd')}
                                className={`p-4 rounded-lg border-2 transition-all ${
                                    documentChoice === 'jd'
                                        ? 'border-purple-500 bg-purple-500/10 text-white shadow-lg shadow-purple-500/20'
                                        : 'border-slate-800 bg-slate-900/50 text-slate-400 hover:border-slate-700 hover:bg-slate-900/80'
                                }`}
                            >
                                <Briefcase className="w-6 h-6 mx-auto mb-2" />
                                <p className="font-semibold text-sm">Job Description Only</p>
                                <p className="text-xs text-slate-500 mt-1">Role-specific</p>
                            </button>

                            <button
                                onClick={() => setDocumentChoice('both')}
                                className={`p-4 rounded-lg border-2 transition-all ${
                                    documentChoice === 'both'
                                        ? 'border-green-500 bg-green-500/10 text-white shadow-lg shadow-green-500/20'
                                        : 'border-slate-800 bg-slate-900/50 text-slate-400 hover:border-slate-700 hover:bg-slate-900/80'
                                }`}
                            >
                                <div className="flex justify-center gap-1 mb-2">
                                    <FileText className="w-5 h-5" />
                                    <Briefcase className="w-5 h-5" />
                                </div>
                                <p className="font-semibold text-sm">Both Documents</p>
                                <p className="text-xs text-slate-500 mt-1">Personalized</p>
                            </button>
                        </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-6">
                        {/* Resume Upload - Show only if needed */}
                        {(documentChoice === 'resume' || documentChoice === 'both') && (
                            <div className="border-2 border-dashed border-slate-800 rounded-xl p-8 text-center hover:border-blue-500/50 transition-all hover:bg-slate-900/50">
                                <input
                                    type="file"
                                    id="resume"
                                    accept=".pdf,.doc,.docx"
                                    onChange={(e) => handleFileUpload(e, 'resume')}
                                    className="hidden"
                                />
                                <label htmlFor="resume" className="cursor-pointer block">
                                    <FileText className="w-16 h-16 mx-auto mb-4 text-blue-400" />
                                    <h3 className="text-xl font-semibold mb-2">Your Resume</h3>
                                    <p className="text-slate-500 text-sm mb-4">PDF, DOC, or DOCX (Max 5MB)</p>
                                    {uploadedResume ? (
                                        <div className="bg-green-500/10 border border-green-500/30 px-4 py-3 rounded-lg inline-flex items-center gap-2">
                                            <CheckCircle className="w-5 h-5 text-green-400" />
                                            <span className="text-sm font-medium">{uploadedResume.name}</span>
                                        </div>
                                    ) : (
                                        <div className="bg-blue-600 hover:bg-blue-700 px-6 py-2 rounded-lg inline-block transition-colors font-medium">
                                            Choose File
                                        </div>
                                    )}
                                </label>
                            </div>
                        )}

                        {/* JD Upload - Show only if needed */}
                        {(documentChoice === 'jd' || documentChoice === 'both') && (
                            <div className="border-2 border-dashed border-slate-800 rounded-xl p-8 text-center hover:border-purple-500/50 transition-all hover:bg-slate-900/50">
                                <input
                                    type="file"
                                    id="jd"
                                    accept=".pdf,.doc,.docx,.txt"
                                    onChange={(e) => handleFileUpload(e, 'jd')}
                                    className="hidden"
                                />
                                <label htmlFor="jd" className="cursor-pointer block">
                                    <Briefcase className="w-16 h-16 mx-auto mb-4 text-purple-400" />
                                    <h3 className="text-xl font-semibold mb-2">Job Description</h3>
                                    <p className="text-slate-500 text-sm mb-4">PDF, DOC, DOCX, or TXT</p>
                                    {uploadedJD ? (
                                        <div className="bg-green-500/10 border border-green-500/30 px-4 py-3 rounded-lg inline-flex items-center gap-2">
                                            <CheckCircle className="w-5 h-5 text-green-400" />
                                            <span className="text-sm font-medium">{uploadedJD.name}</span>
                                        </div>
                                    ) : (
                                        <div className="bg-purple-600 hover:bg-purple-700 px-6 py-2 rounded-lg inline-block transition-colors font-medium">
                                            Choose File
                                        </div>
                                    )}
                                </label>
                            </div>
                        )}
                    </div>
                </div>

                {/* Interview Settings Section */}
                <div className="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700 p-8 mb-6">
                    <h2 className="text-2xl font-semibold mb-6 flex items-center gap-2">
                        <Settings className="w-6 h-6 text-blue-400" />
                        Interview Settings
                    </h2>

                    <div className="grid md:grid-cols-2 gap-6">
                        {/* Duration */}
                        <div>
                            <label className="flex items-center gap-2 text-sm font-medium mb-3">
                                <Clock className="w-4 h-4 text-blue-400" />
                                Interview Duration
                            </label>
                            <select
                                value={interviewSettings.duration}
                                onChange={(e) => setInterviewSettings({...interviewSettings, duration: e.target.value})}
                                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                            >
                                <option value="15">15 minutes (Quick Practice)</option>
                                <option value="30">30 minutes (Standard)</option>
                                <option value="45">45 minutes (Comprehensive)</option>
                                <option value="60">60 minutes (Full Mock)</option>
                            </select>
                        </div>

                        {/* Difficulty */}
                        <div>
                            <label className="flex items-center gap-2 text-sm font-medium mb-3">
                                <Users className="w-4 h-4 text-blue-400" />
                                Difficulty Level
                            </label>
                            <select
                                value={interviewSettings.difficulty}
                                onChange={(e) => setInterviewSettings({...interviewSettings, difficulty: e.target.value})}
                                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                            >
                                <option value="easy">Easy (Entry Level)</option>
                                <option value="medium">Medium (Mid Level)</option>
                                <option value="hard">Hard (Senior Level)</option>
                                <option value="expert">Expert (Leadership)</option>
                            </select>
                        </div>

                        {/* Focus Area */}
                        <div>
                            <label className="flex items-center gap-2 text-sm font-medium mb-3">
                                <MessageSquare className="w-4 h-4 text-blue-400" />
                                Focus Area
                            </label>
                            <select
                                value={interviewSettings.focusArea}
                                onChange={(e) => setInterviewSettings({...interviewSettings, focusArea: e.target.value})}
                                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                            >
                                <option value="technical">Technical Skills</option>
                                <option value="behavioral">Behavioral Questions</option>
                                <option value="balanced">Balanced Mix</option>
                                <option value="communication">Communication Skills</option>
                            </select>
                        </div>

                        {/* Question Count */}
                        <div>
                            <label className="flex items-center gap-2 text-sm font-medium mb-3">
                                <MessageSquare className="w-4 h-4 text-blue-400" />
                                Number of Questions
                            </label>
                            <select
                                value={interviewSettings.questionCount}
                                onChange={(e) => setInterviewSettings({...interviewSettings, questionCount: e.target.value})}
                                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                            >
                                <option value="3">3 Questions</option>
                                <option value="5">5 Questions</option>
                                <option value="7">7 Questions</option>
                                <option value="10">10 Questions</option>
                            </select>
                        </div>
                    </div>

                    {/* Additional Options */}
                    <div className="mt-6 pt-6 border-t border-slate-700">
                        <h3 className="text-sm font-medium mb-4 text-slate-300">Additional Features</h3>
                        <div className="grid md:grid-cols-2 gap-4">
                            <label className="flex items-center gap-3 bg-slate-700/30 p-4 rounded-lg cursor-pointer hover:bg-slate-700/50 transition-all">
                                <input
                                    type="checkbox"
                                    checked={interviewSettings.includeVideo}
                                    onChange={(e) => setInterviewSettings({...interviewSettings, includeVideo: e.target.checked})}
                                    className="w-5 h-5 text-blue-600 bg-slate-700 border-slate-600 rounded focus:ring-2 focus:ring-blue-500"
                                />
                                <div className="flex items-center gap-2">
                                    <Video className="w-4 h-4 text-blue-400" />
                                    <span className="text-sm font-medium">Video Analysis (Eye Contact, Posture)</span>
                                </div>
                            </label>

                            <label className="flex items-center gap-3 bg-slate-700/30 p-4 rounded-lg cursor-pointer hover:bg-slate-700/50 transition-all">
                                <input
                                    type="checkbox"
                                    checked={interviewSettings.includeBehavioral}
                                    onChange={(e) => setInterviewSettings({...interviewSettings, includeBehavioral: e.target.checked})}
                                    className="w-5 h-5 text-blue-600 bg-slate-700 border-slate-600 rounded focus:ring-2 focus:ring-blue-500"
                                />
                                <div className="flex items-center gap-2">
                                    <MessageSquare className="w-4 h-4 text-purple-400" />
                                    <span className="text-sm font-medium">Speech Analysis (Clarity, Confidence)</span>
                                </div>
                            </label>
                        </div>
                    </div>
                </div>

                {/* Action Button */}
                <div className="flex justify-center">
                    <button
                        onClick={handleStartInterview}
                        disabled={!canStartInterview()}
                        className={`px-12 py-4 rounded-xl font-semibold text-lg flex items-center gap-3 transition-all transform hover:scale-105 ${
                            canStartInterview()
                                ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 shadow-xl shadow-blue-500/30'
                                : 'bg-slate-700 cursor-not-allowed opacity-50'
                        }`}
                    >
                        <Video className="w-6 h-6" />
                        Start AI Interview
                    </button>
                </div>

                {!canStartInterview() && (
                    <p className="text-center text-slate-400 text-sm mt-4">
                        {documentChoice === 'both'
                            ? 'Please upload both documents to begin'
                            : documentChoice === 'resume'
                                ? 'Please upload your resume to begin'
                                : 'Please upload job description to begin'}
                    </p>
                )}
            </div>
        </div>
    );
};

export default InterviewSetupPage;