import { Stack } from 'expo-router';

export default function MainLayout() {
  return (
    <Stack
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: '#000000' }
      }}
    >
      <Stack.Screen name="feed" />
    </Stack>
  );
}
