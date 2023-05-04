from tkinter import ttk
from tkinter import *
from index import *
from tkinter import messagebox
root = Tk()
root.geometry("700x250")
frame=Frame(root,bg="skyblue3",width=700,height=300)
frame.pack()
frame.grid()
Label(frame, text="Just write down the prompt and get the blog").grid(column=0, row=0)
textbox=Entry(frame,text="Give your keywords here")
textbox.grid(column=0, row=1)
butt1=ttk.Button(frame, text="Generate Blog",command=lambda: make_blogs_on_press(str(textbox.get())))
butt1.grid(column=1, row=1)
butt2=ttk.Button(frame, text="Generate PPT",command=lambda: make_ppt("user",str(textbox.get())))
butt2.grid(column=0, row=2)
butt3=ttk.Button(frame, text="Generate Video",command=lambda: inc_generate_video(create_blog(str(textbox.get()))))
butt3.grid(column=1, row=2)
butt4=ttk.Button(frame, text="Done",command=lambda: inc_generate_video(create_blog(str(textbox.get()))))
butt4.grid(column=1, row=3)
butt5=ttk.Button(frame, text="Quit", command=root.destroy)
butt5.grid(column=1, row=4)
label=Label(frame, text=f"Once clicked Generate Blog, check Confluence and search for the blog created in minute!!!")
label.grid(column=0, row=3)

root.mainloop()

def make_label():
    label.config(text=f"Created blog in Confluence and Blogin on : {str(textbox.get())}")
    messagebox.showinfo("Message",f"Blog generated on f{textbox.get()}")