import React, { useState } from 'react';
import { useNavigate } from "react-router-dom";
import { Upload, FileText, Briefcase, CheckCircle, Settings, Clock, MessageSquare, Video, Users, Loader2 } from 'lucide-react';

const InterviewSetupPage = () => {
    const [documentChoice, setDocumentChoice] = useState('both');
    const [uploadedResume, setUploadedResume] = useState(null);
    const [uploadedJD, setUploadedJD] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
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
            if (type === 'resume') setUploadedResume(file);
            else setUploadedJD(file);
        }
    };

    const canStartInterview = () => {
        if (documentChoice === 'both') return uploadedResume && uploadedJD;
        if (documentChoice === 'resume') return !!uploadedResume;
        if (documentChoice === 'jd') return !!uploadedJD;
        return false;
    };

    const handleStartInterview = async () => {
        if (!canStartInterview()) return;

        setIsLoading(true);
        setError(null);

        try {
            // Build multipart form — Flask reads files + settings from this
            const formData = new FormData();

            if (uploadedResume) formData.append('resume', uploadedResume);
            if (uploadedJD)     formData.append('jd', uploadedJD);

            // Send settings as a JSON string in the same request
            formData.append('settings', JSON.stringify(interviewSettings));
            formData.append('document_choice', documentChoice);

            const response = await fetch('http://localhost:8080/api/interview/generate-questions', {
                method: 'POST',
                // ✅ Do NOT set Content-Type manually — browser sets it with the boundary
                body: formData,
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || `Server error: ${response.status}`);
            }

            const data = await response.json();
            // data.questions  → array of generated questions
            // data.session_id → unique ID for this interview session

            // Pass questions to the interview page via router state
           navigate(`/interview/session/${data.id}`, { // Changed from data.session_id
                state: {
                    questions: data.questions,
                    settings: interviewSettings,
                }
            });

        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
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

                    <div className="mb-8">
                        <label className="text-sm font-medium mb-3 block text-slate-400">
                            Choose what to upload:
                        </label>
                        <div className="grid grid-cols-3 gap-4">
                            {[
                                { value: 'resume', label: 'Resume Only',        sub: 'General practice',  icon: <FileText className="w-6 h-6 mx-auto mb-2" />,                                       color: 'blue'  },
                                { value: 'jd',     label: 'Job Description Only', sub: 'Role-specific',   icon: <Briefcase className="w-6 h-6 mx-auto mb-2" />,                                      color: 'purple' },
                                { value: 'both',   label: 'Both Documents',     sub: 'Personalized',      icon: <div className="flex justify-center gap-1 mb-2"><FileText className="w-5 h-5" /><Briefcase className="w-5 h-5" /></div>, color: 'green' },
                            ].map(({ value, label, sub, icon, color }) => (
                                <button
                                    key={value}
                                    onClick={() => setDocumentChoice(value)}
                                    className={`p-4 rounded-lg border-2 transition-all ${
                                        documentChoice === value
                                            ? `border-${color}-500 bg-${color}-500/10 text-white shadow-lg shadow-${color}-500/20`
                                            : 'border-slate-800 bg-slate-900/50 text-slate-400 hover:border-slate-700'
                                    }`}
                                >
                                    {icon}
                                    <p className="font-semibold text-sm">{label}</p>
                                    <p className="text-xs text-slate-500 mt-1">{sub}</p>
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-6">
                        {(documentChoice === 'resume' || documentChoice === 'both') && (
                            <UploadBox
                                id="resume"
                                icon={<FileText className="w-16 h-16 mx-auto mb-4 text-blue-400" />}
                                title="Your Resume"
                                hint="PDF, DOC, or DOCX (Max 5MB)"
                                accept=".pdf,.doc,.docx"
                                uploadedFile={uploadedResume}
                                onChange={(e) => handleFileUpload(e, 'resume')}
                                btnColor="bg-blue-600 hover:bg-blue-700"
                                borderHover="hover:border-blue-500/50"
                            />
                        )}
                        {(documentChoice === 'jd' || documentChoice === 'both') && (
                            <UploadBox
                                id="jd"
                                icon={<Briefcase className="w-16 h-16 mx-auto mb-4 text-purple-400" />}
                                title="Job Description"
                                hint="PDF, DOC, DOCX, or TXT"
                                accept=".pdf,.doc,.docx,.txt"
                                uploadedFile={uploadedJD}
                                onChange={(e) => handleFileUpload(e, 'jd')}
                                btnColor="bg-purple-600 hover:bg-purple-700"
                                borderHover="hover:border-purple-500/50"
                            />
                        )}
                    </div>
                </div>

                {/* Interview Settings */}
                <div className="bg-slate-800/50 backdrop-blur rounded-2xl border border-slate-700 p-8 mb-6">
                    <h2 className="text-2xl font-semibold mb-6 flex items-center gap-2">
                        <Settings className="w-6 h-6 text-blue-400" />
                        Interview Settings
                    </h2>
                    <div className="grid md:grid-cols-2 gap-6">
                        <SelectField label="Interview Duration" icon={<Clock className="w-4 h-4 text-blue-400" />}
                            value={interviewSettings.duration}
                            onChange={(v) => setInterviewSettings({ ...interviewSettings, duration: v })}
                            options={[['15','15 minutes (Quick Practice)'],['30','30 minutes (Standard)'],['45','45 minutes (Comprehensive)'],['60','60 minutes (Full Mock)']]}
                        />
                        <SelectField label="Difficulty Level" icon={<Users className="w-4 h-4 text-blue-400" />}
                            value={interviewSettings.difficulty}
                            onChange={(v) => setInterviewSettings({ ...interviewSettings, difficulty: v })}
                            options={[['easy','Easy (Entry Level)'],['medium','Medium (Mid Level)'],['hard','Hard (Senior Level)'],['expert','Expert (Leadership)']]}
                        />
                        <SelectField label="Focus Area" icon={<MessageSquare className="w-4 h-4 text-blue-400" />}
                            value={interviewSettings.focusArea}
                            onChange={(v) => setInterviewSettings({ ...interviewSettings, focusArea: v })}
                            options={[['technical','Technical Skills'],['behavioral','Behavioral Questions'],['balanced','Balanced Mix'],['communication','Communication Skills']]}
                        />
                        <SelectField label="Number of Questions" icon={<MessageSquare className="w-4 h-4 text-blue-400" />}
                            value={interviewSettings.questionCount}
                            onChange={(v) => setInterviewSettings({ ...interviewSettings, questionCount: v })}
                            options={[['3','3 Questions'],['5','5 Questions'],['7','7 Questions'],['10','10 Questions']]}
                        />
                    </div>

                    <div className="mt-6 pt-6 border-t border-slate-700">
                        <h3 className="text-sm font-medium mb-4 text-slate-300">Additional Features</h3>
                        <div className="grid md:grid-cols-2 gap-4">
                            <CheckboxField label="Video Analysis (Eye Contact, Posture)" icon={<Video className="w-4 h-4 text-blue-400" />}
                                checked={interviewSettings.includeVideo}
                                onChange={(v) => setInterviewSettings({ ...interviewSettings, includeVideo: v })}
                            />
                            <CheckboxField label="Speech Analysis (Clarity, Confidence)" icon={<MessageSquare className="w-4 h-4 text-purple-400" />}
                                checked={interviewSettings.includeBehavioral}
                                onChange={(v) => setInterviewSettings({ ...interviewSettings, includeBehavioral: v })}
                            />
                        </div>
                    </div>
                </div>

                {/* Error Banner */}
                {error && (
                    <div className="bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl px-6 py-4 mb-6 text-sm">
                        ⚠️ {error}
                    </div>
                )}

                {/* Start Button */}
                <div className="flex flex-col items-center gap-3">
                    <button
                        onClick={handleStartInterview}
                        disabled={!canStartInterview() || isLoading}
                        className={`px-12 py-4 rounded-xl font-semibold text-lg flex items-center gap-3 transition-all transform hover:scale-105 ${
                            canStartInterview() && !isLoading
                                ? 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 shadow-xl shadow-blue-500/30'
                                : 'bg-slate-700 cursor-not-allowed opacity-50'
                        }`}
                    >
                        {isLoading
                            ? <><Loader2 className="w-6 h-6 animate-spin" /> Generating Questions…</>
                            : <><Video className="w-6 h-6" /> Start AI Interview</>
                        }
                    </button>
                    {!canStartInterview() && !isLoading && (
                        <p className="text-slate-400 text-sm">
                            {documentChoice === 'both'   ? 'Please upload both documents to begin'
                             : documentChoice === 'resume' ? 'Please upload your resume to begin'
                             : 'Please upload a job description to begin'}
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
};

/* ─── Small reusable sub-components ─────────────────────────────────────── */

const UploadBox = ({ id, icon, title, hint, accept, uploadedFile, onChange, btnColor, borderHover }) => (
    <div className={`border-2 border-dashed border-slate-800 rounded-xl p-8 text-center ${borderHover} transition-all hover:bg-slate-900/50`}>
        <input type="file" id={id} accept={accept} onChange={onChange} className="hidden" />
        <label htmlFor={id} className="cursor-pointer block">
            {icon}
            <h3 className="text-xl font-semibold mb-2">{title}</h3>
            <p className="text-slate-500 text-sm mb-4">{hint}</p>
            {uploadedFile ? (
                <div className="bg-green-500/10 border border-green-500/30 px-4 py-3 rounded-lg inline-flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    <span className="text-sm font-medium">{uploadedFile.name}</span>
                </div>
            ) : (
                <div className={`${btnColor} px-6 py-2 rounded-lg inline-block transition-colors font-medium`}>
                    Choose File
                </div>
            )}
        </label>
    </div>
);

const SelectField = ({ label, icon, value, onChange, options }) => (
    <div>
        <label className="flex items-center gap-2 text-sm font-medium mb-3">{icon}{label}</label>
        <select
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className="w-full bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
        >
            {options.map(([val, text]) => <option key={val} value={val}>{text}</option>)}
        </select>
    </div>
);

const CheckboxField = ({ label, icon, checked, onChange }) => (
    <label className="flex items-center gap-3 bg-slate-700/30 p-4 rounded-lg cursor-pointer hover:bg-slate-700/50 transition-all">
        <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)}
            className="w-5 h-5 text-blue-600 bg-slate-700 border-slate-600 rounded focus:ring-2 focus:ring-blue-500" />
        <div className="flex items-center gap-2">{icon}<span className="text-sm font-medium">{label}</span></div>
    </label>
);

export default InterviewSetupPage;