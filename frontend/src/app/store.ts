import { configureStore, ThunkAction, Action } from '@reduxjs/toolkit';
import counterReducer from '../features/counter/counterSlice';
import { setupListeners } from '@reduxjs/toolkit/dist/query';
import { gameCounterApi } from '../services/game-counter';

export const store = configureStore({
  reducer: {
    counter: counterReducer,
    [gameCounterApi.reducerPath]: gameCounterApi.reducer,
  },
  middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(gameCounterApi.middleware),
});

setupListeners(store.dispatch);

export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>;
