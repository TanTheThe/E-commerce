import { useContext, useEffect } from 'react';
import { FaCloudUploadAlt } from 'react-icons/fa';
import { FiX, FiStar } from 'react-icons/fi';
import { IoMdClose } from 'react-icons/io';
import { MyContext } from "../../App";
import { LazyLoadImage } from 'react-lazy-load-image-component';

const EvaluateModal = ({ isOpen, onClose, selectedVariant, onSubmit, evaluateForm, setEvaluateForm }) => {
    const context = useContext(MyContext);

    if (!isOpen) return null;

    const convertToBase64 = (file) => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
        });
    };

    const handleImageUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        try {
            const previewUrl = URL.createObjectURL(file);

            const base64 = await convertToBase64(file);

            const imageData = {
                file: file,
                url: previewUrl,
                name: file.name,
                base64
            };

            setEvaluateForm(prev => ({ ...prev, image: imageData }));
        } catch (error) {
            console.error("Error uploading image:", error);
            if (context?.openAlertBox) {
                context.openAlertBox("error", "Có lỗi xảy ra trong quá trình upload ảnh");
            }
        }
    };

    const removeImage = () => {
        if (evaluateForm.image?.url) {
            URL.revokeObjectURL(evaluateForm.image.url);
        }
        setEvaluateForm(prev => ({ ...prev, image: null }));
    };

    const handleSubmit = () => {
        if (!evaluateForm.rate || evaluateForm.rate === 0) {
            if (context?.openAlertBox) {
                context.openAlertBox("error", "Vui lòng chọn số sao đánh giá!");
            }
            return;
        }

        if (!evaluateForm.comment?.trim()) {
            if (context?.openAlertBox) {
                context.openAlertBox("error", "Vui lòng nhập nhận xét!");
            }
            return;
        }

        onSubmit();
    };

    const handleClose = () => {
        if (evaluateForm.image?.url) {
            URL.revokeObjectURL(evaluateForm.image.url);
        }
        onClose();
    };

    useEffect(() => {
        return () => {
            if (evaluateForm.image?.url) {
                URL.revokeObjectURL(evaluateForm.image.url);
            }
        };
    }, [evaluateForm.image]);

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.4)' }}>
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-gray-800">Đánh giá sản phẩm</h3>
                    <button onClick={handleClose} className="text-gray-500 hover:text-gray-700 cursor-pointer">
                        <FiX className="text-xl" />
                    </button>
                </div>

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Đánh giá sao</label>
                        <div className="flex gap-1">
                            {[1, 2, 3, 4, 5].map(star => (
                                <button
                                    key={star}
                                    onClick={() => setEvaluateForm(prev => ({ ...prev, rate: star }))}
                                    className={`text-2xl cursor-pointer ${star <= evaluateForm.rate ? 'text-yellow-400' : 'text-gray-300'} hover:text-yellow-400 transition-colors`}
                                >
                                    <FiStar className={star <= evaluateForm.rate ? 'fill-current' : ''} />
                                </button>
                            ))}
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Nhận xét</label>
                        <textarea
                            value={evaluateForm.comment}
                            onChange={(e) => setEvaluateForm(prev => ({ ...prev, comment: e.target.value }))}
                            className="w-full p-3 border border-gray-300 rounded-lg resize-none"
                            rows="4"
                            placeholder="Chia sẻ trải nghiệm của bạn về sản phẩm..."
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Hình ảnh (tùy chọn)
                        </label>

                        {!evaluateForm.image ? (
                            <div className="border-dashed border-2 border-gray-300 h-[150px] flex items-center justify-center bg-gray-100 rounded relative hover:border-blue-400 hover:bg-blue-50 transition-colors">
                                <input
                                    type="file"
                                    accept="image/*"
                                    onChange={handleImageUpload}
                                    className="absolute inset-0 opacity-0 z-10 cursor-pointer"
                                    id="evaluate-image-upload"
                                />
                                <label htmlFor="evaluate-image-upload" className="text-center text-gray-500 cursor-pointer">
                                    <FaCloudUploadAlt className="mx-auto mb-2 text-2xl" />
                                    <p className="text-sm font-medium">Nhấp để chọn ảnh</p>
                                    <p className="text-xs">Hỗ trợ định dạng JPG, PNG</p>
                                </label>
                            </div>
                        ) : (
                            <div className="relative w-full h-[150px] border rounded overflow-hidden">
                                <LazyLoadImage
                                    src={evaluateForm.image.url}
                                    alt={evaluateForm.image.name}
                                    className="object-cover w-full h-full"
                                    effect="blur"
                                />
                                <span
                                    onClick={removeImage}
                                    className="absolute top-1 right-1 bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center cursor-pointer hover:bg-red-700 transition-colors"
                                >
                                    <IoMdClose />
                                </span>
                            </div>
                        )}
                    </div>
                </div>

                <div className="flex gap-3 mt-6">
                    <button
                        onClick={handleClose}
                        className="flex-1 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
                    >
                        Hủy
                    </button>
                    <button
                        onClick={handleSubmit}
                        className="flex-1 py-2 bg-[#ff5252] text-white rounded-lg hover:bg-[#e53e3e] transition-colors cursor-pointer"
                    >
                        Gửi đánh giá
                    </button>
                </div>
            </div>
        </div>
    );
};

export default EvaluateModal;