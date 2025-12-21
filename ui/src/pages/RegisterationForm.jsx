import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import logo from '../assets/logo.png';

const RegistrationForm = () => {
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitMessage, setSubmitMessage] = useState({ type: '', text: '' });
    const navigate = useNavigate();

    const {
        register,
        handleSubmit,
        watch,
        formState: { errors }
    } = useForm({
        mode: 'onBlur'
    });

    // Watch password to compare with confirmPassword
    const password = watch("password");

    const onSubmit = async (data) => {
        setIsSubmitting(true);
        setSubmitMessage({ type: '', text: '' });

        try {
            // Adjusted endpoint for registration
            const response = await axios.post('http://localhost:8080/api/auth/register', data);

            if (response.status === 201 || response.status === 200) {
                setSubmitMessage({
                    type: 'success',
                    text: 'Account created successfully! Redirecting to login...'
                });
                setTimeout(() => navigate('/users/login'), 2000);
            }
        } catch (error) {
            setSubmitMessage({
                type: 'error',
                text: error.response?.data?.message || 'Registration failed. Please try again.'
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="h-screen overflow-hidden bg-[#0b1221] flex flex-col items-center justify-center p-4 font-sans antialiased">
            {/* Decorative Glow */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-3xl h-96 bg-indigo-600/10 blur-[120px] pointer-events-none" />

            <div className="w-full max-w-lg z-10">
                <div className="bg-[#111827]/60 backdrop-blur-2xl border border-gray-800 rounded-3xl shadow-2xl p-5 md:p-7">

                    {/* Header */}
                    <div className="text-center mb-8">
                        <div className='w-16 h-16 bg-[#1e293b] rounded-2xl mx-auto mb-4 flex items-center justify-center border border-gray-700 shadow-xl'>
                            <img src={logo} alt='AceView' className="w-10 h-10 object-contain" />
                        </div>
                        <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">Create Account</h1>
                        <p className="text-gray-400">Join AceView and master your interview presence.</p>
                    </div>

                    {/* Feedback Message */}
                    {submitMessage.text && (
                        <div className={`mb-6 p-4 rounded-xl text-sm ${
                            submitMessage.type === 'success'
                                ? 'bg-green-500/10 border border-green-500/20 text-green-400'
                                : 'bg-red-500/10 border border-red-500/20 text-red-400'
                        }`}>
                            {submitMessage.text}
                        </div>
                    )}

                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                            {/* Full Name */}
                            <div>
                                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2 ml-1">Full Name</label>
                                <input
                                    type="text"
                                    placeholder="John Doe"
                                    className={`w-full px-4 py-3 bg-[#0f172a] border rounded-xl text-white placeholder-gray-600 focus:outline-none focus:ring-2 transition-all ${
                                        errors.fullName ? 'border-red-500/50 focus:ring-red-500/10' : 'border-gray-700 focus:border-[#3b82f6] focus:ring-[#3b82f6]/10'
                                    }`}
                                    {...register('username', { required: 'Full name is required' })}
                                />
                            </div>

                            {/* Email */}
                            <div>
                                <label className="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2 ml-1">Email</label>
                                <input
                                    type="email"
                                    placeholder="john@example.com"
                                    className={`w-full px-4 py-3 bg-[#0f172a] border rounded-xl text-white placeholder-gray-600 focus:outline-none focus:ring-2 transition-all ${
                                        errors.email ? 'border-red-500/50 focus:ring-red-500/10' : 'border-gray-700 focus:border-[#3b82f6] focus:ring-[#3b82f6]/10'
                                    }`}
                                    {...register('email', {
                                        required: 'Email is required',
                                        pattern: { value: /^\S+@\S+$/i, message: 'Invalid email' }
                                    })}
                                />
                            </div>
                        </div>

                        {/* Password */}
                        <div>
                            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2 ml-1">Password</label>
                            <input
                                type="password"
                                placeholder="••••••••"
                                className={`w-full px-4 py-3 bg-[#0f172a] border rounded-xl text-white placeholder-gray-600 focus:outline-none focus:ring-2 transition-all ${
                                    errors.password ? 'border-red-500/50 focus:ring-red-500/10' : 'border-gray-700 focus:border-[#3b82f6] focus:ring-[#3b82f6]/10'
                                }`}
                                {...register('password', {
                                    required: 'Password is required',
                                    minLength: { value: 8, message: 'Minimum 8 characters' }
                                })}
                            />
                            {errors.password && <p className="text-[10px] text-red-400 mt-1">{errors.password.message}</p>}
                        </div>

                        {/* Confirm Password */}
                        <div>
                            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2 ml-1">Confirm Password</label>
                            <input
                                type="password"
                                placeholder="••••••••"
                                className={`w-full px-4 py-3 bg-[#0f172a] border rounded-xl text-white placeholder-gray-600 focus:outline-none focus:ring-2 transition-all ${
                                    errors.confirmPassword ? 'border-red-500/50 focus:ring-red-500/10' : 'border-gray-700 focus:border-[#3b82f6] focus:ring-[#3b82f6]/10'
                                }`}
                                {...register('confirmPassword', {
                                    required: 'Please confirm your password',
                                    validate: (value) => value === password || "Passwords do not match"
                                })}
                            />
                            {errors.confirmPassword && <p className="text-[10px] text-red-400 mt-1">{errors.confirmPassword.message}</p>}
                        </div>

                        {/* Terms Checkbox */}
                        <div className="flex items-start space-x-3 py-2">
                            <input
                                type="checkbox"
                                className="mt-1 rounded bg-[#0f172a] border-gray-700 text-[#4f46e5] focus:ring-[#4f46e5]/20"
                                {...register('terms', { required: true })}
                            />
                            <span className="text-xs text-gray-400 leading-tight">
                I agree to the <button type="button" className="text-[#3b82f6] hover:underline">Terms of Service</button> and <button type="button" className="text-[#3b82f6] hover:underline">Privacy Policy</button>.
              </span>
                        </div>

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className='w-full py-4 rounded-xl font-bold text-white bg-gradient-to-r from-[#4f46e5] to-[#7c3aed] hover:scale-[1.01] active:scale-[0.99] transition-all shadow-lg shadow-indigo-500/20 flex items-center justify-center space-x-2'
                        >
                            {isSubmitting ? (
                                <div className="h-5 w-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            ) : (
                                <>
                                    <span>Create Account</span>
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                                    </svg>
                                </>
                            )}
                        </button>
                    </form>

                    {/* Footer */}
                    <div className="mt-8 text-center border-t border-gray-800 pt-6">
                        <p className="text-sm text-gray-500">
                            Already have an account?{' '}
                            <Link to="/users/login" className="text-white font-semibold hover:text-[#3b82f6] transition-colors">
                                Sign In
                            </Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RegistrationForm;