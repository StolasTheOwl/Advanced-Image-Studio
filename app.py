import streamlit as st
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
import segno
import io
import base64

# 1. Page layout and header setup[cite: 1]
st.set_page_config(page_title="Universal Media Workspace", page_icon="⚙️", layout="wide")

# ==========================================
# WORKSPACE NAVIGATION
# ==========================================
st.sidebar.title("🗂️ Workspace Navigation")
app_mode = st.sidebar.radio(
    "Select Engine:",
    ["🎨 Advanced Image Studio", "🔮 Universal QR Engine"]
)
st.sidebar.markdown("---")

# ==========================================
# MODE A: ADVANCED IMAGE STUDIO
# ==========================================
if app_mode == "🎨 Advanced Image Studio":
    st.title("🎨 Advanced Image Studio")
    st.write("Upload any image file from your computer and apply beautiful visual filters instantly![cite: 1]")
    
    # File Uploader Component: Allows picking a local photo file[cite: 1]
    uploaded_file = st.file_uploader("Choose an image file...", type=["jpg", "jpeg", "png"]) #[cite: 1]
    
    if uploaded_file is not None:
        try:
            # Open the uploaded binary file data as a structured PIL Image object[cite: 1]
            original_image = Image.open(uploaded_file)
            max_w, max_h = original_image.size
            
            # --- Sidebar Controls ---
            st.sidebar.header("✂️ Direct Manipulation Tools")
            
            # Crop Boundaries
            st.sidebar.subheader("Crop (Pixels)")
            col_c1, col_c2 = st.sidebar.columns(2)
            left = col_c1.number_input("Left", 0, max_w-1, 0)
            right = col_c2.number_input("Right", 0, max_w-1, 0)
            top = col_c1.number_input("Top", 0, max_h-1, 0)
            bottom = col_c2.number_input("Bottom", 0, max_h-1, 0)
            
            # Resize
            st.sidebar.subheader("Resize (Dimensions)")
            col_r1, col_r2 = st.sidebar.columns(2)
            new_w = col_r1.number_input("Width", 1, 10000, max_w)
            new_h = col_r2.number_input("Height", 1, 10000, max_h)
            
            # Compression Engine
            st.sidebar.header("🗜️ Image Compression Engine")
            quality_slider = st.sidebar.slider("Output Quality (%)", 1, 100, 85)
            
            # Sidebar Filter Selector Tray[cite: 1]
            st.sidebar.header("⚙️ Filter Control Panel") #[cite: 1]
            selected_filter = st.sidebar.selectbox(
                "Choose a Visual Filter Effect:", #[cite: 1]
                [
                    "Original", "Black & White", "Sepia Tone", "Gaussian Blur", 
                    "Contour Sketch", "Vibrant Saturation", "Retro Negative", "Emboss Art"
                ]
            )
            
            # --- Image Processing Pipeline ---
            processed_image = original_image.copy()
            
            # Apply Crop
            if (left + right < max_w) and (top + bottom < max_h):
                processed_image = processed_image.crop((left, top, max_w - right, max_h - bottom))
            else:
                st.warning("⚠️ Invalid crop bounds detected. Bypassing crop step.")
                
            # Apply Resize
            if (new_w, new_h) != processed_image.size:
                processed_image = processed_image.resize((new_w, new_h))
            
            # Apply Filters
            if selected_filter == "Black & White":
                # ImageOps.grayscale converts standard color pixels into single-channel gray values[cite: 1]
                processed_image = ImageOps.grayscale(processed_image)
            elif selected_filter == "Sepia Tone":
                # A quick trick to make sepia: turn to grayscale, then tint it with a warm brown overlay[cite: 1]
                gray = ImageOps.grayscale(processed_image) #[cite: 1]
                processed_image = ImageOps.colorize(gray, "#704214", "#C0B283") #[cite: 1]
            elif selected_filter == "Gaussian Blur":
                # Applies a smooth smoothing convolution filter matrix over pixels[cite: 1]
                processed_image = processed_image.filter(ImageFilter.GaussianBlur(radius=5)) #[cite: 1]
            elif selected_filter == "Contour Sketch":
                # Finds high-contrast structural edges to create a rough pencil outline effect[cite: 1]
                processed_image = processed_image.filter(ImageFilter.CONTOUR) #[cite: 1]
            elif selected_filter == "Vibrant Saturation":
                enhancer = ImageEnhance.Color(processed_image)
                processed_image = enhancer.enhance(2.5)
            elif selected_filter == "Retro Negative":
                # Convert to RGB safely before inverting to prevent alpha channel crashes
                if processed_image.mode != 'RGB':
                    processed_image = processed_image.convert('RGB')
                processed_image = ImageOps.invert(processed_image)
            elif selected_filter == "Emboss Art":
                processed_image = processed_image.filter(ImageFilter.EMBOSS)

            # Apply Compression & Encode for metrics
            img_byte_arr = io.BytesIO()
            save_image = processed_image.convert('RGB') if processed_image.mode != 'RGB' else processed_image
            save_image.save(img_byte_arr, format='JPEG', quality=quality_slider)
            img_bytes = img_byte_arr.getvalue()
            
            original_byte_arr = io.BytesIO()
            original_image.convert('RGB').save(original_byte_arr, format='JPEG', quality=100)
            original_size_kb = len(original_byte_arr.getvalue()) / 1024
            new_size_kb = len(img_bytes) / 1024

            # --- Canvas Rendering ---
            st.markdown("### 📊 Live Compression Metrics")
            m1, m2, m3 = st.columns(3)
            m1.metric("Original Size", f"{original_size_kb:.2f} KB")
            m2.metric("New Optimized Size", f"{new_size_kb:.2f} KB")
            reduction_percentage = (1 - new_size_kb/original_size_kb) * 100 if original_size_kb > 0 else 0
            m3.metric("Total Reduction", f"{reduction_percentage:.2f} %", f"{reduction_percentage:.1f}%")

            st.markdown("---")
            
            # Display the Original vs Processed images side-by-side using web columns[cite: 1]
            col1, col2 = st.columns(2) #[cite: 1]
            with col1:
                st.markdown("### 📸 Original Image") #[cite: 1]
                st.image(original_image, use_container_width=True) #[cite: 1]
            with col2:
                st.markdown(f"### ✨ {selected_filter} Result") #[cite: 1]
                st.image(img_bytes, use_container_width=True) #[cite: 1]
                
            # Download Engine
            st.download_button(
                label="📥 Download Filtered Image", #[cite: 1]
                data=img_bytes, #[cite: 1]
                file_name="filtered_photo.jpg", #[cite: 1]
                mime="image/jpeg" #[cite: 1]
            )
            
        except Exception as e:
            st.error(f"⚠️ Convolution/Processing Error: {str(e)}")
            st.stop()
            
    else:
        st.info("💡 Standby: Please upload a photo file from your device to activate the image canvas filters.[cite: 1]")


# ==========================================
# MODE B: UNIVERSAL QR ENGINE
# ==========================================
elif app_mode == "🔮 Universal QR Engine":
    st.title("🔮 Universal QR Engine")
    st.write("Generate high-capacity QR codes dynamically from text, absolute links, or embedded Base64 image strings.")
    
    # Sidebar Styling Overrides
    st.sidebar.header("🎨 Styling Overrides")
    qr_line_color = st.sidebar.color_picker("QR Line Color (Dark)", "#000000")
    qr_bg_color = st.sidebar.color_picker("Canvas Background Color (Light)", "#FFFFFF")
    
    # Structural Pipelines
    st.markdown("### ⚙️ Select Encoding Pipeline")
    pipeline = st.radio("Choose the QR code function:", 
                        ["Text to QR", "Link to QR", "Image to QR (Convert Image to QR)"],
                        horizontal=True)
    st.markdown("---")
    
    qr_data = None
    
    if pipeline == "Text to QR":
        st.markdown("#### 📝 Raw Text Encoding")
        qr_data = st.text_area("Input raw paragraphs here. Scanners will render this literal text natively:", height=150)
        
    elif pipeline == "Link to QR":
        st.markdown("#### 🔗 Absolute Link Redirect")
        qr_data = st.text_input("Input the absolute URL destination:")
        
    elif pipeline == "Image to QR (Convert Image to QR)":
        st.markdown("#### 🖼️ Binary to Base64 URI Encoding")
        st.warning("⚠️ High-Capacity Mode Warning: Standard QR matrices top out around 3KB of raw data. To prevent matrix overflow crashes, please upload heavily compressed icons or low-resolution thumbnails.")
        
        img_upload = st.file_uploader("Upload Image to Base64-Encode into QR Payload", type=["png", "jpg", "jpeg"])
        if img_upload is not None:
            try:
                bytes_data = img_upload.getvalue()
                encoded_string = base64.b64encode(bytes_data).decode('utf-8')
                mime_type = img_upload.type
                # Build the complete Base64 URI scheme
                qr_data = f"data:{mime_type};base64,{encoded_string}"
                st.success(f"✅ Image successfully transcoded. Payload Length: {len(qr_data)} characters.")
            except Exception as e:
                st.error(f"⚠️ Base64 Encoding Fault: {str(e)}")
                
    # QR Generation & Download Pipeline
    if qr_data:
        if st.button("🚀 Compile QR Matrix", type="primary"):
            try:
                # Generate matrix using Segno Engine
                qr = segno.make(qr_data)
                
                out = io.BytesIO()
                qr.save(out, kind='png', dark=qr_line_color, light=qr_bg_color, scale=10)
                out.seek(0)
                
                st.markdown("### 🖨️ Matrix Output Render")
                col_qr, col_empty = st.columns([1, 2])
                with col_qr:
                    st.image(out, caption="Dynamically Compiled QR Code", use_container_width=True)
                
                st.download_button(
                    label="📥 Download Compiled QR Code",
                    data=out,
                    file_name="universal_qr.png",
                    mime="image/png"
                )
            except segno.helpers.DataOverflowError:
                st.error("🛑 Data Overflow Error: The Base64 string payload vastly exceeds maximum standard QR capacity. Please resize/compress the image file significantly before uploading.")
            except Exception as e:
                st.error(f"⚠️ Matrix Generation Fault: {str(e)}")
