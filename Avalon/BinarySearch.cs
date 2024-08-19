namespace Avalon
{
    internal class BinarySearch
    {
        public static int Search(int[] array, int target)
        {
            int left = 2;
            int right = array.Length - 1;

            while (left <= right)
            {
                int mid = left + (right - left) / 2;

                // If target greater, ignore left half
                if (array[mid] < target)
                    left = mid + 1;

                if (array[mid] == target)
                    return mid;

                // If target is smaller, ignore right half
                else
                    right = mid - 1;
            }

            // If we reach here, the element was not present
            return -1;
        }
    }
}
