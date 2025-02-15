import win32ui
import win32gui
import win32con
import win32api
from PIL import Image
import os
from pathlib import Path

def extract_icon_from_exe(exe_path, save_path):
    try:
        # Load the exe icon
        ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
        ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
        
        large, small = win32gui.ExtractIconEx(str(exe_path), 0)
        if not large and not small:
            return None
            
        if large:
            win32gui.DestroyIcon(large[0])
        if small:
            win32gui.DestroyIcon(small[0])
            
        # Load the icon
        ico_handle = win32gui.ExtractIcon(0, str(exe_path), 0)
        if not ico_handle:
            return None
        
        try:
            # Create a DC and bitmap to draw the icon
            hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
            hbmp = win32ui.CreateBitmap()
            hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
            hdc_mem = hdc.CreateCompatibleDC()
            
            # Select bitmap into DC
            old_bitmap = hdc_mem.SelectObject(hbmp)
            
            # Draw the icon
            hdc_mem.DrawIcon((0, 0), ico_handle)
            
            # Convert to PIL Image
            bmpstr = hbmp.GetBitmapBits(True)
            img = Image.frombuffer(
                'RGBA',
                (ico_x, ico_y),
                bmpstr, 'raw', 'BGRA', 0, 1
            )
            
            # Save the image
            img.save(save_path)
            
            # Cleanup
            hdc_mem.SelectObject(old_bitmap)  # Restore the old bitmap
            win32gui.DeleteObject(hbmp.GetHandle())  # Delete the bitmap
            hdc_mem.DeleteDC()  # Delete the memory DC
            hdc.DeleteDC()  # Delete the DC
            
            return save_path
            
        finally:
            # Always destroy the icon handle
            win32gui.DestroyIcon(ico_handle)
            
    except Exception as e:
        print(f"Failed to extract icon: {e}")
        return None 