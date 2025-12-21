import axios from 'axios';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import logo from '../assets/logo.png'; // Make sure this is the AceView logo

export default function LoginForm() {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitMessage, setSubmitMessage] = useState({ type: '', text: '' });
    const navigate = useNavigate();

    const {
        register,
        handleSubmit,
        formState: { errors}
    } = useForm({
        mode: 'onBlur',
        defaultValues: {
            email: '',
            password: ''
        }
    });

    const onSubmit = async (data) => {
        setIsSubmitting(true);
        setSubmitMessage({ type: '', text: '' });

        try {
            const response = await axios.post('http://localhost:8080/api/auth/login', data, {
                withCredentials: true
            });

            // Axios puts the backend JSON inside response.data
            if (response.status === 200) {
                const { userId, username } = response.data;

                setSubmitMessage({
                    type: 'success',
                    text: `Welcome ${username}! Redirecting...`
                });

                // Navigate using the ID, not the full name
                setTimeout(() => navigate(`/users/${userId}`), 1500);
            }
        } catch (error) {
            setSubmitMessage({
                type: 'error',
                text: error.response?.data?.message || 'Invalid credentials. Please try again.'
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        // Deep Navy Background
        <div className="min-h-screen bg-[#0b1221] flex flex-col items-center justify-center p-4 font-sans antialiased">

            {/* Optional: Subtle Glow Background Effect */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-2xl h-64 bg-blue-600/10 blur-[120px] pointer-events-none" />

            <div className="w-full max-w-md z-10">
                <div className="bg-[#111827]/50 backdrop-blur-xl border border-gray-800 rounded-3xl shadow-2xl p-10">

                    {/* Brand Header */}
                    <div className="text-center mb-10">
                        <div className='w-20 h-20 bg-[#1e293b] rounded-2xl mx-auto mb-4 flex items-center justify-center shadow-inner border border-gray-700'>
                            <img src={logo} alt='AceView Logo' className="w-12 h-12 object-contain" />
                        </div>
                        <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">
                            Welcome to <span className="text-[#3b82f6]">AceView</span>
                        </h1>
                        <p className="text-gray-400 text-sm">Perfect your presence. Enter your details.</p>
                    </div>

                    {/* Feedback Messages */}
                    {submitMessage.text && (
                        <div className={`mb-6 p-3 rounded-xl text-sm transition-all ${
                            submitMessage.type === 'success'
                                ? 'bg-green-500/10 border border-green-500/20 text-green-400'
                                : 'bg-red-500/10 border border-red-500/20 text-red-400'
                        }`}>
                            {submitMessage.text}
                        </div>
                    )}

                    <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-5">
                        {/* Email Field */}
                        <div>
                            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 ml-1">
                                Email Address
                            </label>
                            <input
                                type="email"
                                placeholder="name@company.com"
                                className={`w-full px-4 py-3.5 bg-[#0f172a] border rounded-xl text-white placeholder-gray-600 focus:outline-none focus:ring-2 transition-all ${
                                    errors.email
                                        ? 'border-red-500/50 focus:ring-red-500/20'
                                        : 'border-gray-700 focus:border-[#3b82f6] focus:ring-[#3b82f6]/20'
                                }`}
                                {...register('email', {
                                    required: 'Email is required',
                                    pattern: { value: /^\S+@\S+$/i, message: 'Invalid email' }
                                })}
                            />
                            {errors.email && <span className="text-xs text-red-400 mt-1 ml-1">{errors.email.message}</span>}
                        </div>

                        {/* Password Field */}
                        <div>
                            <div className="flex justify-between mb-2 ml-1">
                                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider">
                                    Password
                                </label>
                                <button type="button" className="text-xs text-[#3b82f6] hover:underline">Forgot?</button>
                            </div>
                            <input
                                type="password"
                                placeholder="••••••••"
                                className={`w-full px-4 py-3.5 bg-[#0f172a] border rounded-xl text-white placeholder-gray-600 focus:outline-none focus:ring-2 transition-all ${
                                    errors.password
                                        ? 'border-red-500/50 focus:ring-red-500/20'
                                        : 'border-gray-700 focus:border-[#3b82f6] focus:ring-[#3b82f6]/20'
                                }`}
                                {...register('password', { required: 'Password is required' })}
                            />
                            {errors.password && <span className="text-xs text-red-400 mt-1 ml-1">{errors.password.message}</span>}
                        </div>

                        {/* Submit Button - Gradient Style from Hero Page */}
                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className='w-full py-4 px-4 rounded-xl font-bold text-white bg-gradient-to-r from-[#4f46e5] to-[#7c3aed] hover:opacity-90 transition-all shadow-lg shadow-indigo-500/20 flex items-center justify-center space-x-2'
                        >
                            {isSubmitting ? (
                                <div className="h-5 w-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            ) : (
                                <>
                                    <span>Sign In</span>
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                                    </svg>
                                </>
                            )}
                        </button>
                    </form>

                    {/* Footer */}
                    <div className="mt-8 text-center">
                        <p className="text-sm text-gray-500">
                            New to AceView?{' '}
                            <button className="text-white font-semibold hover:text-[#3b82f6] transition-colors" onClick={()=>{navigate("/users/new")}}>
                                Create an account
                            </button>
                        </p>
                    </div>
                </div>

                {/* Decorative stats footer (optional, matches hero vibe) */}
                <div className="mt-8 flex justify-center space-x-8 opacity-40 grayscale">
                    <span className="text-[10px] text-white uppercase tracking-widest">2.5K+ Members</span>
                    <span className="text-[10px] text-white uppercase tracking-widest">98% Happy</span>
                </div>
            </div>
        </div>
    );
}