import './App.css'
import { createBrowserRouter, RouterProvider } from "react-router-dom"
import DashBoard from './Pages/DashBoard'
import Header from './Components/Header'
import Sidebar from './Components/Sidebar'
import React, { createContext, useState } from 'react'
import Login from './Pages/Login'
import SignUp from './Pages/SignUp'
import Products from './Pages/Products'

import Dialog from '@mui/material/Dialog';
import ListItemText from '@mui/material/ListItemText';
import ListItemButton from '@mui/material/ListItemButton';
import List from '@mui/material/List';
import Divider from '@mui/material/Divider';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import { IoMdClose } from 'react-icons/io'
import Slide from '@mui/material/Slide';
import Button from '@mui/material/Button'
import AddProduct from './Pages/Products/addProduct'
import HomeSliderBanners from './Pages/HomeSliderBanners'
import AddHomeSlide from './Pages/HomeSliderBanners/addHomeSlide'
import CategoryList from './Pages/Category/CategoryList'
import AddCategory from './Pages/Category/addCategory'
import Users from './Pages/Users'
import Orders from './Pages/Orders'
import Verify from './Pages/Verify'
import toast, { Toaster } from 'react-hot-toast'
import ForgotPassword from './Pages/ForgotPassword'
import ResetPasswordEmail from './Pages/ResetPasswordEmail'
import ResetPasswordOtp from './Pages/ResetPasswordOtp'
import SendEmailGetOtp from './Pages/SendEmailGetOtp'
import ResetPassword from './Pages/ResetPassword'
import useAuth from './Pages/Verify/auth'
import Profile from './Pages/Profile'
import EditProduct from './Pages/Products/editProduct'
import SpecialOffer from './Pages/SpecialOffer'
import ReviewProduct from './Pages/Review'

const Transition = React.forwardRef(function Transition(
  props, ref) {
  return <Slide direction="up" ref={ref} {...props} />;
});

const MyContext = createContext()

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)

  const { isLogin, setIsLogin, userData, setUserData, isLoading, checkLogin } = useAuth();

  const [isOpenFullScreenPanel, setIsOpenFullScreenPanel] = useState({
    open: false,
    model: ''
  })

  const router = createBrowserRouter([
    {
      path: "/",
      exact: true,
      element: (
        <>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <DashBoard />
              </div>
            </div>
          </section>
        </>
      )
    },
    {
      path: "/login",
      exact: true,
      element: (
        <>
          <Login />
        </>
      )
    },
    {
      path: "/signup",
      exact: true,
      element: (
        <>
          <SignUp />
        </>
      )
    },
    {
      path: "/verify",
      exact: true,
      element: (
        <>
          <Verify />
        </>
      )
    },
    {
      path: "/forgot-password",
      exact: true,
      element: (
        <>
          <ForgotPassword />
        </>
      )
    },
    {
      path: "/forgot-password-email",
      exact: true,
      element: (
        <>
          <ResetPasswordEmail />
        </>
      )
    },
    {
      path: "/forgot-password-otp",
      exact: true,
      element: (
        <>
          <ResetPasswordOtp />
        </>
      )
    },
    {
      path: "/send-mail",
      exact: true,
      element: (
        <>
          <SendEmailGetOtp />
        </>
      )
    },
    {
      path: "/reset-password/:token",
      exact: true,
      element: (
        <>
          <ResetPassword />
        </>
      )
    },
    {
      path: "/products",
      exact: true,
      element: (
        <>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <Products />
              </div>
            </div>
          </section>
        </>
      )
    },
    {
      path: "/homeSlider/list",
      exact: true,
      element: (
        <>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <HomeSliderBanners />
              </div>
            </div>
          </section>
        </>
      )
    },
    {
      path: "/category/list",
      exact: true,
      element: (
        <>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <CategoryList />
              </div>
            </div>
          </section>
        </>
      )
    },
    {
      path: "/users",
      exact: true,
      element: (
        <>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <Users />
              </div>
            </div>
          </section>
        </>
      )
    },
    {
      path: "/orders",
      exact: true,
      element: (
        <>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <Orders />
              </div>
            </div>
          </section>
        </>
      )
    },
    {
      path: "/profile",
      exact: true,
      element: (
        <>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <Profile />
              </div>
            </div>
          </section>
        </>
      )
    },
    {
      path: "/special-offer/list",
      exact: true,
      element: (
        <>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <SpecialOffer />
              </div>
            </div>
          </section>
        </>
      )
    },
    {
      path: "/reviews/list",
      exact: true,
      element: (
        <>
          <section className='main'>
            <Header />
            <div className='contentMain flex'>
              <div className={`overflow-hidden sidebarWrapper ${isSidebarOpen === true ? 'w-[15%]' : 'w-[0px] opacity-0'} transition-all`}>
                <Sidebar />
              </div>
              <div className={`contentRight py-4 px-5 ${isSidebarOpen === false ? 'w-[100%]' : 'w-[85%]'} transition-all`}>
                <ReviewProduct />
              </div>
            </div>
          </section>
        </>
      )
    },
  ])

  const openAlertBox = (status, msg) => {
    if (status === "success") {
      toast.success(msg)
    }
    if (status === "error") {
      toast.error(msg)
    }
  }

  const values = {
    isSidebarOpen,
    setIsSidebarOpen,
    isLogin,
    setIsLogin,
    isOpenFullScreenPanel,
    setIsOpenFullScreenPanel,
    openAlertBox,
    userData,
    setUserData,
    isLoading,
    checkLogin
  }

  return (
    <>
      <MyContext.Provider value={values}>
        <RouterProvider router={router} />
        <Toaster position="top-center" reverseOrder={false} />
        <Dialog
          fullScreen
          open={isOpenFullScreenPanel.open}
          onClose={() => setIsOpenFullScreenPanel({
            open: false
          })}
          slots={{
            transition: Transition,
          }}
        >
          <AppBar sx={{ position: 'relative' }}>
            <Toolbar>
              <IconButton
                edge="start"
                color="inherit"
                onClick={() => setIsOpenFullScreenPanel({
                  open: false
                })}
                aria-label="close"
              >
                <IoMdClose className='text-gray-800' />
              </IconButton>
              <Typography sx={{ ml: 2, flex: 1 }} variant="h6" component="div">
                <span className='text-gray-800'>{isOpenFullScreenPanel?.model}</span>
              </Typography>
            </Toolbar>
          </AppBar>
          {
            isOpenFullScreenPanel?.model === 'Add Product' && <AddProduct />
          }
          {
            isOpenFullScreenPanel?.model === 'Add Home Slide' && <AddHomeSlide />
          }
          {
            isOpenFullScreenPanel?.model === 'Add New Category' && <AddCategory />
          }
          {isOpenFullScreenPanel?.model === 'Update Product' && (
            <EditProduct
              productId={isOpenFullScreenPanel?.productId}
              onClose={() => setIsOpenFullScreenPanel({ open: false })}
            />
          )}
        </Dialog>
      </MyContext.Provider>
    </>
  )
}

export default App
export { MyContext }
