import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { FeedProvider } from '../providers/FeedProvider';

export default function RootLayout() {
  return (
    <FeedProvider>
      <StatusBar style="dark" />
      <Stack
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: '#ffffff' }
        }}
      >
        <Stack.Screen name="index" />
        <Stack.Screen name="onboarding" />
        <Stack.Screen name="(main)" />
      </Stack>
    </FeedProvider>
  );
}
